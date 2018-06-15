#ifndef SimList_CUH
#define SIMLIST_CUH
#include <thrust/host_vector.h>
#include <thrust/device_vector.h>
#include <thrust/copy.h>
#include <string>

#include "Types.cuh"
struct base_n{
    static size_t used_host_mem;
};

template<typename T>
struct SimList1D: base_n{
    size_t n;

    thrust::device_vector<T> d;
    thrust::host_vector<T> h;

    T* devPtr;
    T* hostPtr;

    SimList1D(size_t _n): n(_n), h(_n, 0), d(_n, 0){
        base_n::used_host_mem += n*sizeof(T);
        devPtr = thrust::raw_pointer_cast(&d[0]);
        hostPtr = thrust::raw_pointer_cast(&h[0]);
    }

    ~SimList1D(){
        base_n::used_host_mem -= n*sizeof(T);
        devPtr = NULL;
        hostPtr = NULL;
    }

    // copy constructor
    SimList1D(const SimList1D& other): n(other.n), d(other.n), h(other.n){
        thrust::copy(other.d.begin(), other.d.end(), d.begin());
        thrust::copy(other.h.begin(), other.h.end(), h.begin());
    }

    // copy assignment
    SimList1D& operator=(const SimList1D& other){
        thrust::copy(other.d.begin(), other.d.end(), d.begin());
        thrust::copy(other.h.begin(), other.h.end(), h.begin());
    }

    void CopyToDevice(size_t _n, size_t offset){
        thrust::copy(h.begin()+offset, h.begin()+offset+_n, d.begin()+offset);
    }

    void CopyToDevice(){
        CopyToDevice(n, 0);
    }

    void CopyToHost(size_t _n, size_t offset){
        thrust::copy(d.begin()+offset, d.begin()+offset+_n, h.begin()+offset);
    }

    void CopyToHost(){
        CopyToHost(n, 0);
    }

};

// special constructor for angles3 list
template<>
SimList1D<angles3>::SimList1D(size_t _n): n(_n), h(_n), d(_n){
    base_n::used_host_mem += 3*sizeof(real)*n;
    devPtr = thrust::raw_pointer_cast(&d[0]);
    hostPtr = thrust::raw_pointer_cast(&h[0]);
}

template<typename T>
struct SimList3D{
    size_t n;

    SimList1D<T> x; 
    SimList1D<T> y; 
    SimList1D<T> z;

    R3Nptrs devPtrs; 
    R3Nptrs hostPtrs; 
    
    SimList3D(size_t _n): n(_n), x(_n), y(_n), z(_n){
        devPtrs.x = x.devPtr;
        devPtrs.y = y.devPtr;
        devPtrs.z = z.devPtr;
        
        hostPtrs.x = x.hostPtr;
        hostPtrs.y = y.hostPtr;
        hostPtrs.z = z.hostPtr;
    }
    
    ~SimList3D(){
        devPtrs.x = NULL;
        devPtrs.y = NULL;
        devPtrs.z = NULL;
        
        hostPtrs.x = NULL;
        hostPtrs.y = NULL;
        hostPtrs.z = NULL;
    }

    // copy constructor
    SimList3D(const SimList3D& other): n(other.n), x(other.x), y(other.y),
                                       z(other.z){
    }

    // copy assignment
    SimList3D& operator=(const SimList3D& other){
        n = other.n;
        x = other.x;
        y = other.y;
        z = other.z; 
    }

    void CopyToDevice(size_t _n, size_t offset){
        x.CopyToDevice(_n, offset);
        y.CopyToDevice(_n, offset);
        z.CopyToDevice(_n, offset);
    }

    void CopyToDevice(){
        x.CopyToDevice(n, 0);
        y.CopyToDevice(n, 0);
        z.CopyToDevice(n, 0);
    }

    void CopyToHost(size_t _n, size_t offset){
        x.CopyToHost(_n, offset);
        y.CopyToHost(_n, offset);
        z.CopyToHost(_n, offset);
    }

    void CopyToHost(){
        x.CopyToHost(n, 0);
        y.CopyToHost(n, 0);
        z.CopyToHost(n, 0);
    }

};
#endif // SimList_CU
