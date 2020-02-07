#include "wrapper.hpp"

Streamkm::Streamkm(unsigned int coresetsize,unsigned int length){
	this->coresetsize=coresetsize;
	this->length=length;
	manager.buckets=NULL;
	timestamp=0;
	dim=0;
}
Streamkm::~Streamkm(){
	//still may leak
	if(manager.buckets==NULL)
		return;
	for(int i=0;i<manager.numberOfBuckets;i++){
		struct Bucket bucket=manager.buckets[i];
		freePoint(bucket.points);
		freePoint(bucket.spillover);
		free(bucket.points);
		free(bucket.spillover);
		free(manager.buckets+i);
	}
	free(manager.buckets);
}
void Streamkm::batch_online_cluster(ndarray batch){
	auto buff=batch.request();
	if(buff.ndim!=2)
		throw std::runtime_error("batch must be a matrix");
	unsigned int lines=buff.shape[0];
	if(dim==0){
		dim=buff.shape[1];
		initManager(&manager,length,dim,coresetsize);
	}
	else if(dim!=buff.shape[1])
		throw std::runtime_error("batch must have a consistent number of columns");
	double* ptr=(double*)buff.ptr;
	struct point p;
	initPoint(&p,dim);
	p.weight=1.0;
	for(unsigned int i=0;i<lines;i++){
		p.squareSum=0;
		for(unsigned int j=0;j<dim;j++){
			double number=ptr[j];
			p.coordinates[j]=number;
			p.squareSum+=number*number;
		}
		p.id=timestamp;
		insertPoint(&p,&manager);

		timestamp++;
		ptr+=dim;
	}
	freePoint(&p);
}
ndarray Streamkm::get_streaming_coreset_centers(){
	ndarray ans(coresetsize*dim);
	double* ptr=(double*)ans.request().ptr;

	struct point *streamingCoreset = getCoresetFromManager(&manager,dim);
	for(unsigned int i=0;i<coresetsize;i++){
		struct point coreset = streamingCoreset[i];
		for(unsigned int j=0;j<dim;j++){
			ptr[j]=coreset.coordinates[j]/coreset.weight;
		}
		ptr+=dim;
	}

	ans.resize({(size_t)coresetsize,(size_t)dim});
	return ans;
}
