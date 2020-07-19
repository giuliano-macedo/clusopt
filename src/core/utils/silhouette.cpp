/*
<%
setup_pybind11(cfg)
cfg['compiler_args'] = ['-std=c++11','-Wall','-O2']
%>
*/

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

namespace py = pybind11;

#include <vector>
#include <cmath>
#include <limits>

typedef py::array_t<double,py::array::c_style| py::array::forcecast> ndarray_double;
typedef py::array_t<int,py::array::c_style| py::array::forcecast> ndarray_int;

typedef unsigned int uint;

#define INF std::numeric_limits<double>::infinity()

#define DOUBLE_NAN std::numeric_limits<double>::quiet_NaN()

double c_distance(double* a,double* b,unsigned int dim){
	double ans=0;
	for(unsigned int i=0;i<dim;i++){
		double diff=b[i]-a[i];
		ans+=diff*diff;
	}
	return sqrt(ans);
}

class Accumulator{

private:
	double sum_;
	uint n;

public:
	Accumulator():sum_(0),n(0){}

	void add(double value){
		sum_+=value;
		n++;
	}

	double mean(){
		if(n==0)return DOUBLE_NAN;
		return (double)sum_/n;
	}

	void reset(){
		sum_=0;
		n=0;
	}
};

class Silhouette{

private:
	std::vector<Accumulator> table;
	Accumulator score_accum;
	uint dim;
	uint k;

public:
	Silhouette(uint n_clusters):table(n_clusters),score_accum(),dim(0),k(n_clusters){}

	double get_score(uint no_samples,double* dataset,int* labels){
		double* point_i=dataset;
		int* label_i=labels;

		for(uint i=0;i<no_samples;i++){
			//----------------------------------------------------
			//compute ai,bi
			double* point_j=dataset;
			int* label_j=labels;
			for(uint j=0;j<no_samples;j++){ //n^2, can be optimized to triangle
				if(i!=j)
					table[*label_j].add(c_distance(point_i,point_j,dim));
				point_j+=dim;
				label_j++;
			}

			double ai=table[*label_i].mean();
			double bi=INF;

			for(uint j=0;j<k;j++){
				double m=table[j].mean();
				table[j].reset();
				if(j==(uint)*label_i)continue;
				if(m<bi)
					bi=m;
			}

			//----------------------------------------------------
			double s=(bi-ai)/fmax(ai,bi);
			score_accum.add(std::isnan(s)?0:s);
			
			point_i+=dim;
			label_i++;
		}
		double ans=score_accum.mean();
		score_accum.reset();
		return ans;
	}

	double get_score_py(ndarray_double dataset,ndarray_int labels){
		auto dataset_buff=dataset.request();
		auto labels_buff=labels.request();

		if(dataset_buff.ndim!=2)
			throw std::runtime_error("dataset must be a matrix");
		if(labels_buff.ndim!=1)
			throw std::runtime_error("labels must be a vector");
		if(labels_buff.shape[0]!=dataset_buff.shape[0])
			throw std::runtime_error("incosistent number of samples");
		if(dim==0)
			dim=dataset_buff.shape[1];
		else if(dim!=dataset_buff.shape[1])
			throw std::runtime_error("dataset must have a consistent number of columns");
		
		return get_score(
			labels_buff.shape[0],
			(double*)dataset_buff.ptr,
			(int*)labels_buff.ptr
		);
	}	
};
PYBIND11_MODULE(silhouette, m) {
	py::class_<Silhouette>(m, "Silhouette")
		.def(py::init<int>(),py::arg("n_clusters"))
		.def("get_score",&Silhouette::get_score_py)
	;
}