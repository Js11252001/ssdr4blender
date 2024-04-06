# SSDR4Blender
* <A href="https://github.com/mukailab/ssdr4maya">SSDR4Maya</A>移植到Blender的版本
* 将顶点动画转换为骨骼动画的插件



## 支持环境
* Windows XP及以上版本（如果能自行编译DLL，则也支持Mac/Linux）
* 支持32/64位的Blender2.65及以上版本（如果修改bl_info，也许能在2.5.0以上版本运行）
* Python3～（使用普通的cdecl调用的dll，通过ctypes调用。Python版本变化时无需重新编译）

## 安装方法
*将bin文件夹中的已编译包全部复制到<A href="https://wiki.blender.org/index.php/Doc:JA/2.6/Manual/Extensions/Python/Add-Ons">Blender的addons文件夹中</A>

## 使用须知
* 请先对变化的Modifier进行Bake。
* 请先对Cloth/Softbody Physics进行Bake。<A href="http://blender.stackexchange.com/questions/42910/how-to-bake-object-with-cloth-simulation-and-subsurf-not-applied-having-troub">标准的Bake功能是没有的。请通过.mdd转换为Shape-key动画。加载.mdd后，请一定要从Physics标签中禁用物理计算（否则会产生双重效果）</A>

###使用步骤
1. 选择处理的形状。
2. 从菜单[Object]->[SSDR]开始处理。
3. 处理完成后，可以在左下角调整参数。请将numMaxIterations设置为满意的最小值。如果顶点数较少导致结果异常，请尝试减少numMinBones。

### 计算参数的调整


- numMinBones： 用于顶点动画近似的最小骨骼数量
- numMaxIterations： 最大迭代次数
- numMaxInfluences： 每个顶点最多分配的骨骼数量

通过改变这三个参数，可以观察到计算结果的变化。当前，我们已经确认如果给最小骨骼数量设置较大值，计算会出错。

## 构建和执行方法
* 扩展库ssdr.dll需要外部库[Eigen](http://eigen.tuxfamily.org/ "Eigen")、 [QuadProg++](http://quadprog.sourceforge.net/ "QuadProg++")。
* 安装Eigen时不需要使用CMake！（这会花费很长时间，并且不需要编译。只需在Include文件夹中设置即可）
* 请在QuadProg++.cc的727行左右的void cholesky_decomposition(Matrix<double>& A)函数中，将throw～、exit(-1);这两行注释掉


### 构建步骤

1. 设置包含Eigen安装文件夹的路径。
4. 下载QuadProg++并将以下四个文件复制到ssdr文件夹中。
 * QuadProg++.hh
 * QuadProg++.cc
 * Array.hh
 * Array.cc
5. 在Visual Studio上构建和执行
