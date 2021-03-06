# anti-NSFW-detection-test
一些尝试用于对抗色情图片检测算法的思路

## 背景

诸如新浪微博和tumblr之类的网站都会对用户上传的图片进行检测，以屏蔽掉某些不合时宜的（Not Suitable for Work）图片。尽管对于某些以此为生的媒体来说这无异于灭顶之灾，但对普通用户而言，类似的检测算法却影响甚小。即便如此，你仍然会感到不爽，尤其是某些时候你想要分享的性感图片也被屏蔽掉。所以使用了一些图片对新浪微博/Tencent AI/Baidu AI的检测算法进行了测试，得出了一些（可能）可行的对抗检测的思路。

## 一些对抗思路

1. 旋转。

   因为基于CNN的检测算法通常是旋转不鲁棒的，所以可以通过将图片旋转一定的角度用于改变概率的预测值。
   
   在早期时，某些平台的检测算法确实存在此问题，但是这一问题很快就被修复。在训练CNN模型时，只需要增加对图片的随机旋转增广就可以改善模型的旋转鲁棒性。
   
   以Tencent AI的色情图片检测为例，将示例图片分别旋转90°和180°之后进行测试，porn的概率反而越来越大。这说明了这一种思路目前已经不太可行。
   
   ![不同旋转角度下的检测结果比对示意图](/images/image_at_different_degrees.jpg)
   
2. 拼接空白图片

   多数情况下CNN对于输入图片的尺寸是有限制的，因此在对图片进行检测时一般会首先将其缩放为1:1的正方形图片，然后再进行检测。针对这样的图片预处理方法，我们可以将原始图片和一张较长的空白图片拼接在一起组成一张长宽比远大于1的图片。这样的图片在缩放成正方形后会偏离模型训练数据集的数据分布，因此可以起到对抗的作用。
   
   然而这样方式也可以很快得到修复。对于长宽比大大偏离1:1的图片，我们只需要将图片切分为多张1:1的图片然后分别对其检测即可。
   
   对于这样的对抗方式，从下面的示意图可以看出Baidu AI和Tencent AI可能因为处理方式不同而得出了截然不同的检测结果。
   
   ![不同平台下的长图检测结果对比示意图](/images/leng_image_at_different_platforms.jpg)
   
   P.S. 目前，新浪的算法对这种对抗方式也没有进行针对性改进。
   P.P.S. 将多张图片拼接在一起也可以对抗算法的检测，但是由于大部分平台会对长图进行大幅度的压缩，因此会有较为严重的质量损失，所以拼接空白图片可能更好。
   P.P.P.S. 这样的一种对抗思路应该不难想到，但是由于针对性的处理方法会增加数倍的计算量，这可能是平台没有进行改进的原因。
  
3. 转为gif图片
   
   将一张空白的图片和一张目标图片分别作为gif图片的两帧，空白帧设置较短的时长，目标图片设置为较长的时长。这样得到的gif图片在点击查看时的效果和正常图片差别很小（缺点是图片的体积大大增加）。
   
   这样的对抗方式理论上非常容易检测到，算法只需要将gif逐帧解析，逐帧分析计算，最后返回最大概率即可。
   
   然而事实是，Baidu AI提供了针对gif色情图片的检测（其接口说明：该请求用于鉴定GIF图片的色情度，对于非gif接口，请使用图像审核组合接口。接口会对图片中每一帧进行识别，并返回所有检测结果中色情值最大的为结果。目前支持三个维度：色情、性感、正常。），Tencent AI不支持gif格式的图片，新浪微博也没有对此进行改进。
   
   ![带有空白帧的gif图片示意图](/images/model_1.gif)
   
   P.P.P.P.S. 正如之前提到的，对此类对抗行为针对性的改进会大大增加平台的计算开销。考虑到微博上有非常多的正常图片（搞笑gif或者视频转置的gif等等）均为gif格式，要对所有的gif进行类似的检测会增加很多成本。
   
4. 条纹化&gif化
   
   根据一定的条纹间隔，将图片的横向的像素值交替设置为255/0。
   
   除非在训练过程中也加入类似的图片增广手段，否则算法很难准确判断此类图片的类别。但这样的对抗手段存在的问题是，图片的观感会受到一定程度的影响。条纹宽度越宽，越不容易被检测到，但信息损失带来的观感下降也会越严重。为了缓解这一问题，可能需要将两张条纹化的图片叠加在一起组成gif以弥补这一缺陷。
   
   条纹宽度为1时，Tencent AI的检测结果为正常；条纹宽度为16时，Baidu AI的检测结果也是正常。
   
   ![条纹宽度为1的图片在Tencent AI的检测结果](/images/detection_result_at_tencent.png)
   
   ![条纹宽度为16的图片在Baidu AI的检测结果](/images/detection_result_at_baidu.png)
   
   将两张条纹化的图片帧拼接在一起组成gif后尽管观感略有提升，但是由于gif帧率限制导致的频闪会引起不适感。
   
   ![拼接条纹化图片得到的gif图片示意图](/images/model_2.gif)

5. 利用GAN进行对抗攻击

   在之前的某些论文中，研究人员训练了一些生成模型用于攻击CNN分类模型。训练得到的模型通过向图片中添加一些人眼不敏感的噪音，从而改变了图片的分类概率。通过训练类似的模型，我们也可以通过向NSFW图片中添加噪音以改变其预测概率。
   
   然而由于我们无法得到平台所使用的模型（即便是黑箱状态的），所以想要训练得到这样的一个模型是非常困难的。而且即便我们真的可以得到这样的模型，平台也可以通过重新训练得到新的模型来对抗我们的攻击。更为无解的问题是，即便我们能够得到所有的模型所对应的对抗模型，平台也只需要在模型之间进行随机切换就可以减轻对抗模型的攻击。
   
   ![一种对CNN分类模型进行攻击的示意图](/images/GAN_CNN.png)

## 一个脚本

在这里，我编写了一个简单的python脚本用于生成两种形式的gif,调用方法为：`python image2gif.py --mode 1/2 --image your_image_path`。

其中`--mode 1`代表生成第一种gif（添加空白帧），`--mode 2`代表生成第二种gif(条纹化之后进行拼接)；`--image your_image_path`指定图片路径，生成的gif和原始图片位于统一路径当中。
