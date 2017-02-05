#include <vector>
#include <map>
#include <string>
//#include <boost/python.hpp>

#include "SSDR.h"

#define DLLEXPORT extern "C" __declspec(dllexport)

SSDR::Output ssdrOutput;

DLLEXPORT double build(int numMinBones, int numMaxInfluences, int numMaxIterations, float *bindVertices, float *animVertices, int numVertices, int numFrames)
{
    SSDR::Parameter ssdrParam;
    ssdrParam.numMaxInfluences = numMaxInfluences;
    ssdrParam.numMaxIterations = numMaxIterations;
    ssdrParam.numMinBones = numMinBones;

    SSDR::Input ssdrInput;
    ssdrInput.numVertices = numVertices;
    ssdrInput.numExamples = numFrames;
    ssdrInput.bindModel.resize(ssdrInput.numVertices);
    ssdrInput.sample.resize(ssdrInput.numVertices * numFrames);
    for (int vid = 0; vid < ssdrInput.numVertices; ++vid)
    {
        ssdrInput.bindModel[vid].x = bindVertices[vid * 3 + 0];
        ssdrInput.bindModel[vid].y = bindVertices[vid * 3 + 1];
        ssdrInput.bindModel[vid].z = bindVertices[vid * 3 + 2];
    }
    for (int f = 0; f < numFrames; ++f)
    {
        for (int vid = 0; vid < ssdrInput.numVertices; ++vid)
        {
            ssdrInput.sample[f * numVertices + vid].x = animVertices[(f * numVertices + vid) * 3 + 0];
            ssdrInput.sample[f * numVertices + vid].y = animVertices[(f * numVertices + vid) * 3 + 1];
            ssdrInput.sample[f * numVertices + vid].z = animVertices[(f * numVertices + vid) * 3 + 2];
        }
    }

    double sqe = SSDR::Decompose(ssdrOutput, ssdrInput, ssdrParam);
    return std::sqrt(sqe / ssdrInput.numVertices);
}

DLLEXPORT double* getSkinningWeight()
{
    size_t num = ssdrOutput.weight.size();
    double *skinningWeight = (double *)malloc(sizeof(double) * num);
    if(skinningWeight==NULL)return NULL;
    
    size_t i=0;
    for (auto it = ssdrOutput.weight.begin(); it != ssdrOutput.weight.end(); ++it,i++)
    {
        skinningWeight[i]=*it;
    }
    return skinningWeight;
}

DLLEXPORT int* getSkinningIndex()
{
    size_t num = ssdrOutput.index.size();
    int *skinningIndex = (int *)malloc(sizeof(int) * num);
    if(skinningIndex==NULL)return NULL;
    
    size_t i=0;
    for (auto it = ssdrOutput.index.begin(); it != ssdrOutput.index.end(); ++it,i++)
    {
        skinningIndex[i]=*it;
    }
    return skinningIndex;
}

DLLEXPORT int getNumBones()
{
    return ssdrOutput.numBones;
}

DLLEXPORT float* getBoneTranslation(int boneIdx, int frame)
{
    float *retval = (float *)malloc(sizeof(float) * 3);
    if(retval==NULL)return NULL;
    
    retval[0]=ssdrOutput.boneTrans[frame * ssdrOutput.numBones + boneIdx].Translation().x;
    retval[1]=ssdrOutput.boneTrans[frame * ssdrOutput.numBones + boneIdx].Translation().y;
    retval[2]=ssdrOutput.boneTrans[frame * ssdrOutput.numBones + boneIdx].Translation().z;
    return retval;
}

DLLEXPORT float* getBoneRotation(int boneIdx, int frame)
{
    float *retval = (float *)malloc(sizeof(float) * 4);
    if(retval==NULL)return NULL;
    
    retval[0]=ssdrOutput.boneTrans[frame * ssdrOutput.numBones + boneIdx].Rotation().x;
    retval[1]=ssdrOutput.boneTrans[frame * ssdrOutput.numBones + boneIdx].Rotation().y;
    retval[2]=ssdrOutput.boneTrans[frame * ssdrOutput.numBones + boneIdx].Rotation().z;
    retval[3]=ssdrOutput.boneTrans[frame * ssdrOutput.numBones + boneIdx].Rotation().w;
    return retval;
}

DLLEXPORT void freeRetArr(void *p)
{
  free(p);
}
