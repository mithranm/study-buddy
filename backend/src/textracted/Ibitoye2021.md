<p>A Brief Review of Convolutional Neural 
Network Techniques for Masked Face 
Recognition  </p>
<p>Abstract— Masked face recognition is now an essential part of 
health safety, security and surveillance systems which offers 
incredible advantages in our daily lives, especially in the era of the 
pandemic ushered in by the outbreak of coronavirus disease in the 
year 2019 (COVID -19). Applications such as; face mask 
compliance checks, facial security checks, facial attendance 
records and facial authentication for access c ontrol now requires 
an effective masked face recognition system. The existing systems 
of masked face recognition were developed to automatically detect 
and understand faces occluded with masks using computer vision 
and deep learning techniques, the systems  are yet to work 
effectively in real -time. This study gives an analysis of some 
techniques used for the implementation of masked face 
recognition system, with emphasis on Convolutional Neural 
Network (CNN). The strengths and enhancement areas of the 
highli ghted techniques towards real -time implementation were 
discussed.<br />
Keywords —detection, image processing, masked face, occlusion, 
recognition<br />
I.INTRODUCTION 
The outbreak of COVID -19 pandemic has introduced 
new ways of living, one of which is wearing of face m ask in 
public places. Studies on coronavirus proved that wearing face 
masks offers a double barrier against the transmission of the 
virus [1]. However, the use of face mask in public places 
compromises security of lives and pr operties as criminals can 
successfully hide their faces under the pretense of using face 
masks [2] 
The advent of coronavirus pandemic has also made face 
recognition a preferred security authentication system. 
Password and fingerprint activated security systems are no 
longer encouraged as they are likely to increase the spread of 
the virus through physical contacts. Security and authentication 
systems that are face activated does not require physical 
contact.<br />
The existing sy stems of masked face recognition have 
not been implemented for real -time usage [3], [4], [2], [5]. It is 
now important to review the curren t techniques for masked face 
recognition with the view of determining improvement areas on 
the system for real -time capabilities.  In recent times, computer vision applications have been 
highly engaged via deep learning techniques. In [4], deep 
learning was defined as a deep neural network which has 
several layers, the layers enable the model to learn dir ectly from 
input data. A deep learning technique used mostly for object 
detection and image processing is the Convolutional Neural 
Network (CNN) [4].<br />
Many researchers have worked with CNN in recent 
years, due to its numerous potentials for solving problems 
related to object detection, object classification and optical 
recognition. CNN was considered in [4] as “a special 
architecture of artificial neural networks and the top -
performing model” which  currently has many applications in 
face mask detection and masked face recognition systems.<br />
This paper gives a review of techniques for image 
acquisition, image preprocessing, masked face detection and 
masked face recognition. The paper also analyses some  CNN -
based techniques for masked face recognition systems.<br />
The remaining part of this paper is organized as follows. 
Section two provides a literature survey of the techniques 
engaged in all involved stages from image acquisition to 
masked face recognitio n. Section three highlighted the 
strengths and the enhancement areas of the reviewed 
techniques. The paper was concluded in the last section which 
suggests areas of future research.<br />
II.REVIEW OF RELATED LITERATURE
A typical system for the detection of masks o n faces and 
recognition of faces occluded with masks is presented in Fig.1. 
The block diagram is crafted from the system diagrams 
presented in [6] and [2]. The system started with image 
acquisition and adaptation of the images before feeding the 
detector. The detector takes in the preprocessed images for face 
and face accessories detection. After an accurate detection, the 
masked faces components are properly analyzed towards 
accurate recognition of the face behind the mask.  Oladapo Ibitoye<br />
Electrical/Electronics and Computer<br />
Engineering Department<br />
Afe Babalola University  Ado Ekiti,<br />
Nigeria<br />
ibitoyeo@abuad.edu.ng<br />
2021 IEEE Concurrent Processes Architectures and Embedded Systems Virtual Conference 978-1-7281-6683-4/21/$31.00 ©2021 IEEE2021 IEEE Concurrent Processes Architectures and Embedded Systems Virtual Conference (COPA) | 978-1-7281-6683-4/21/$31.00 ©2021 IEEE | DOI: 10.1109/COPA51043.2021.9541448
Authorized licensed use limited to: George Mason University. Downloaded on March 16,2024 at 16:55:29 UTC from IEEE Xplore.  Restrictions apply.  </p>
<p>Fig.1: A typical block diagram of face detection and masked 
face recognition system (crafted from the system diagrams 
presented in [6] and [2]. 
A. Image Acquisition and Pre -processing<br />
 Images are gener ally acquired via camera and other 
integrated components such as ultrasonic sensor and 
microcontroller to automate the process. In [9], camera view 
angle and human head alignment were put into consideration 
to compliment the robustness of the Dlib’s fronta l face 
detector.<br />
 In order to prepare the acquired images for accurate 
detection, some image preprocessing techniques are required. 
Brightness change was achieved on the captured face images 
in [7], by obtaining one dark and o ne bright version of each 
image after rotation using equation (1).<br />
𝐼𝑛𝑒𝑤 = 𝛼𝐼𝑜𝑟𝑖𝑔𝑖𝑛𝑎𝑙  + β                                                          (1)   <br />
where, Ioriginal  is the original image intensity and Inew is the 
new intensity after the operation. 𝛼=1.0,1.5 were used to 
obtain dark and bright images respectively, while β  =−15,30<br />
were used to obtain dark and bright images respectively [7]. 
  A cropping filter was applied in [8] to obtain only the 
informative regions of the masked face. This was achieved by 
normalizing all face images into 240 by 240 pixels. The 
resultant image was later partitioned into blocks to divide the 
image into 100 fixed -size square blocks. Only the blocks 
including the non -masked region were extracted. The rotation 
of the face was corrected to remove the masked region 
efficiently.<br />
 For real -time deployment of a masked face recognition 
system, factors such as quality and posit ion of the camera, 
pictorial quality of the faces to be detected and variations in 
environmental conditions are very key to the performance of 
the system.<br />
B. Masked Face Detection and Extraction<br />
 This involves the detection of the presence of human faces 
and cropping out of the entire face region including the area 
covered with mask. Several techniques have been used for face 
detection and extraction such as; Region Proposal Network 
(RPN), Histogram of Oriented Gradients (HOG) based 
detector, linear classifier  detector, sliding window detection 
scheme and ‘OpenCV’ face detector which uses the Viola -
Jones algorithm. <br />
 In [7], Dlib’s face detector was used to detect human face. 
A better detection result was achieved despite some 
chall enging situations. Gaussian Mixture -Model (GMM) based 
foreground/background segmentation algorithm was used for 
facial extraction. This algorithm gave binary mask for the driver’s face. Cloth verification ratio was obtained using 
equation (2) [7]. 
𝑅=𝑁𝑏𝑎𝑐𝑘𝑔𝑟𝑜𝑢𝑛𝑑 /𝑁𝑡𝑜𝑡𝑎𝑙                                                               (2)                              <br />
where, N background  and N total is the total background pixels, and 
the overall pixel count of the selected cloth region, 
respectively. R is the verification ratio.<br />
 In [9], three approaches were introduced for face 
detection. The first approach is boost -based face detection 
which engages boosted cascade Haar features and Normalized 
Pixels Difference. The second approach is Deformable Part 
Model -based which models deformation of faces. The third 
approach is CNN -based which learn the features directly from 
the input image.<br />
 In [10], the authors used locally linear embedding with 
CNN to recognize masked faces. They also introduce a masked 
faces (MAFA) dataset with 30,811 Internet images. Each 
image in MAFA contains at least one face occluded by various 
types of masks which also includes faces covered with hand or 
other objects. A detector model which engaged YOLOv2 
architecture was proposed in [3], the detector utilized ResNet -
50 for feature extraction and  detection. A novel framework 
using MTCNN and VGG -16 for masked face detection was 
also proposed in [11] and [12]. 
 A method for masked face recognition was proposed in<br />
[12], the system integrated a cropping -based method with “the 
Convolutional Block Attention Module (CBAM)”. The best 
cropping is obtained for each case, while the CBAM module 
focuses on eye regions. The system utilized the standard 
MTCNN to detect the fac e of all input images and the key 
points of two eyes. The aligned face images were obtained after 
performing similarity transformation. This was followed by 
cropping of individual image using various scales [12] 
 Fully Convolu tional Neural Network was utilized in [13] 
to detect multiple faces in an image. Many face detection 
techniques were proposed in previous related works which 
utilizes single -stage and double -stage approaches. According 
to [13], these techniques are inefficient for masked faces 
recognition.<br />
 YOLOv3 was used in [14] to detect faces, a deep learning 
architecture named darknet -19 was engaged. The authors used 
wider face and  ‘Celebi’ databases to train the model. In [6], the 
authors developed a face mask identification system using the 
‘SRCNet’ classification network. The system evaluation shows 
an accuracy of 98.7% for face image classification i nto three 
categories, which distinguished faces into three groups, the 
people with appropriate face mask, followed by people with 
inappropriate face masks and the third group was the people 
without face mask.<br />
 A Single Shot Multi -Box Detector (SSD) was pr oposed in 
[15] for face mask detection in public places. The SSD model 
was pre -trained on the MSCOCO dataset for object detection.<br />
Authors in [5] also proposed a Single Shot Multi -Box Detector 
as a face detector, they utilized MobilenetV2 a rchitecture as the 
framework for the classifier. Transfer learning techniques were 
used in [16] to fine -tune a detector model similar to SSD.<br />
Image 
Acquisition 
and 
Preprocessing   </p>
<p>Masked 
Face 
Detection  </p>
<p>Masked Face 
Segmentation 
and 
Recognition  </p>
<p>Authorized licensed use limited to: George Mason University. Downloaded on March 16,2024 at 16:55:29 UTC from IEEE Xplore.  Restrictions apply. C. Masked Face Segmentation and Recognition<br />
 A classical machine learning method for re cognition 
of masked and non -masked face using Principal Component 
Analysis was implemented in [17]. From the system evaluation, 
the method is efficient for non -mask faces recognition while the 
efficiency decreases when applied  to masked faces. Authors in 
[18] proposed a GAN -based network to remove mask objects 
in facial images.  Two discriminants were used in the network: 
The global structure of the masked faces was extracted by the 
first discrimin ant, while the second discriminant extract only 
the missing region from the masked face.<br />
A CNN -based face classifier was used in [7] to verify and 
grant vehicles drivers’  access. In [19], region pr oposal network 
was used to scan the facial images using sliding windows over 
the anchors. Intersection over union (IOU) overlap was used to 
check the similarity of the particular bounding box with the 
other bounding boxes using equation (3).<br />
𝐼𝑂𝑈 =𝐴𝑟𝑒𝑎 𝑜𝑓 𝑜𝑣𝑒𝑟𝑙𝑎𝑝  𝑜𝑓 𝑐𝑜𝑚𝑝𝑎𝑟𝑒  𝑏𝑜𝑥𝑒𝑠 <br />
𝐴𝑟𝑒𝑎  𝑜𝑓 𝑢𝑛𝑖𝑜𝑛  𝑜𝑓 𝑐𝑜𝑚𝑝𝑎𝑟𝑒  𝑏𝑜𝑥𝑒𝑠                    (3) 
In [20], a novel face detection model FSG -FD was used to 
solve the problem of occluded face de tection. The impact of 
features of un -occluded face region was enhanced by the FSG -
FD to classify tasks using region generation method.  VGG16 
pre-trained model was utilized as the backbone network. 
Several datasets were engaged for experiments and results 
shows an improvement of 9.4% over that of faster RCNN on 
wider dataset.<br />
 In [2], a deep learning model was proposed based on 
InceptionV3 architecture. Due to lack of sufficient dataset, the 
authors utilized image augmentation t echniques for 
performance and ‘training data diversity’ enhancement. The 
last layer of the pre -trained inceptionV3 architecture was 
replaced by additional five fine -tuned layers. The additional 
layers are “an average pooling layer with a pool size equal to  5 
x 5”, a ﬂattening layer, a dense layer of 128 neurons, a 
“decisive dense layer with two neurons” and “softmax 
activation function” is added for masked face and unmasked 
face classification. The transfer learning model was trained for 
80 epochs with each  epoch having 42 steps.<br />
 Deep features were extracted from masked faces using 
VGG -16 face CNN descriptor from the 2D images in [8]. The 
model was trained on ImageNet dataset which has over 14 
million images and 1000 classes. Th e VGG -16 architecture has 
16 layers. Its layers consist  of “convolutional layers, Max 
Pooling layers, Activation layers and Fully connected layers” 
[8]. 
 A system called “maskedFaceNet” was proposed in [9], 
the system was inspired by a feed -forward SSD approach, a 
collection of fixed size bounding boxes and scores that are 
obtained for every detected object class instance. The 
predictions were sent to non -maximum suppression layer for 
final d etection computation.<br />
 In [21], a CNN model was proposed for recognition of 
faces with masks. The proposed model has a simple 
architecture with a “convolution layer, an activation layer, a pooling layer, a fully connected layer , and a softmax layer”. 
The multi -layered system was developed to detect face masks 
and recognize masked faces separately. The authors engaged 
publicly available datasets to train the model.<br />
Faster RCNN framework was used for generic object 
detection in [22], several effective strategies for improving the 
Faster RCNN algorithm were proposed. These strategies were 
able to resolve face detection tasks such as; “multi -scale 
training”, “hard negative mining”, and “proper configurat ion of 
anchor sizes for RPN”.<br />
 In [23], a system that integrated convolutional LSTM 
(ConvLSTM) algorithm with fully convolutional networks 
(FCN) was proposed. The model worked on a per -sequence 
basis and takes advantage of the temporal correlation in video 
clips. The developed system was converted from FCN model 
with the replacement of classification layer by ‘ConvLSTM’ 
layers. The training process was simplified by training the FCN 
mode l with all the training images.<br />
 One of th e major challenges in the development of a 
system of masked face recognition is getting dataset. Authors 
in [24] developed a dataset for masked faces and made it 
available publicly. Also, an open -source  tool, “MaskTheFace” 
was used in [25] to mask face images thereby creating large 
dataset of masked faces towards training the facial recognition 
system. More of dataset creation will have positive impact in 
this domain of research.<br />
 However, only a few  research works have been reported 
on masked face recognition. Not many of the current works 
were implemented in real -time.<br />
III. SELECTED  CNN -BASED  TECHNIQUES:<br />
WEAKNESSES  AND  ENHANCEMET  AREAS<br />
Table I show selected CNN -based techniques with analysis 
of the weaknesses and enhancement areas on the techniques.<br />
TABLE I.  SELECTED CNN -BASED TECHNIQUES : WEAKNESSES AND 
ENHANCEMENT AREAS<br />
Ref. Techniques  Weaknesses  Enhancement Areas<br />
[6], 
[14]. 
  CNN -based 
YOLOv3 with 
Darknet -53 as 
feature 
extractor.<br />
 Individual image 
processed had 
different spatial 
compression, this 
increased the 
complexity of the 
system.  A more suitable 
feature extractor e.g., 
Feature Pyramid 
Network will offer 
deep convolution with 
a minimal complexity 
and real time 
capability.<br />
[15], 
[5], 
[9]. CNN -based 
SSD using 
MobilenetV2 
architecture as 
the backbone.  The architecture 
utilized three 
layers for two 
blocks, this made 
the inference time 
relatively slow.  Replacing the detector 
with SSDLite will 
increase the inference 
speed and fortified the 
system for real time 
implementation.<br />
[2],<br />
[8], 
[21]. VGG -16 
Descriptor<br />
using 
InceptionV3 
architecture as 
backbone  VGG -16 descriptor 
has 16 layers 
which works better 
with only a GPU 
based system.  Replacing the 
descriptor with 
SSDLite will make 
the system operational 
on CPU based system.<br />
Authorized licensed use limited to: George Mason University. Downloaded on March 16,2024 at 16:55:29 UTC from IEEE Xplore.  Restrictions apply. IV. CONCLUSION<br />
Some advances in CNN -based masked face recognition 
system were presented in this paper. The study analyzed the 
individual stage of the masked face reco gnition systems. The 
weaknesses and possible areas of improvement on some of the 
selected CNN -techniques were discussed. However, further 
improvements are required to facilitate real -time 
implementation of the systems. Areas such as; deeper learning 
framew orks for masked face recognition, unsupervised masked 
face recognition, fast coding programming frameworks for 
masked face recognition system, deep CNN models with the 
capacity to recognize faces from partly observed masked face 
images and reliable recogni tion of masked faces in complex 
conditions can be looked into.<br />
REFERENCES <br />
[1]  M. Abboah -Offei, Y. Salifu, B. Adewale, J. Bayuo, R. Ofosu -Poku and 
E. Opare -Lokko, "A rapid review of the use of face mask in preventing 
the spread of COVID -19," International Journal of Nursing Studies 
Advances, vol. 3, 2020.<br />
[2]  G. J. Chowdary, N. S.  Punn, S. K. Sonbhadra and S. Agarwal, "Face 
Mask Detection using Transfer Learning of Inception V3," Springer, 
2020.<br />
[3]  M. Loey, G. Manogaran, M. N. Taha and N. E. M. Khalifa, "Fighting 
Against COVID -19: A Novel Deep Learning Model Based on YOLO 
v2 wi th ResNet -50 for Medical Face Mask Detection," Elsevier, 2020.<br />
[4]  Y. Said, "Pynq -YOLO -Net: An Embedded Quantized Convolutional 
Neural Network for Face Mask Detection in COVID -19 Pandemic 
Era," (IJACSA) International Journal of Advanced Computer Science<br />
and Applications, 2020.<br />
[5]  P. Nagrath, R. Jain, A. Madan, R. Arora, P. Kataria and J. Hemanth, "A 
real time DNN -based face mask detection system using single shot 
multibox detector and MobileNetV2," Elevier, 2021.<br />
[6]  B. Qin and D. Li, "Identifying Facemask -Wearing Condition Usin g 
Image Super -Resolution with Classification Network to Prevent 
COVID -19," Sensors, MDPI, 2020.<br />
[7]  D. Ekberjan and A. S. Albert, "Continuous Real -Time Vehicle Driver 
Authentication Using Convolutional Neural Network Based Face 
Recognition," IEEE, 2018.<br />
[8]  W. Hariri, "Efficient Masked Face Recognition Method During the 
Covid -19 Pandemic," IEEE, 2020. <br />
[9]  P. Shitala, Y. Li, D. Lin and D. Sheng, "maskedFaceNet: A Progressive 
Semi -Supervised Masked Face Detector," in WACV , 2021.<br />
[10]  G. Shiming, J. Li, Q. Ye and Z. Luo, "Detecting Masked Faces in the 
wild," CVPR,, pp. 2682 -2690, 2017.<br />
[11]  Y. Qi ting, "Masked face detection via a novel framework," in 
International Conference on Mechanical, Electronic, Control and 
Automation Engineeering , 2018.<br />
[12]  L. Yande, K. Guo, Y. Lu and L. Liu, "Cropping and attention based 
approach for masked face Recogn ition," Springer, 2021.<br />
[13]  Y. Jang, H. Gunes and I. Patras, "Registration -free face -ssd: Single shot 
analysis of smiles, facial attributes, and affect in the wild.," Computer 
Vision and Image Understanding, vol. 182, pp. 17 -29, 2019.<br />
[14]  C. Li, R. Wang, J. Li and L. Fei, "Face detection based on yolov3. In: 
Recent Trends in Intelligent Computing, Communication and Devices," 
Springer, pp. 277 -284, 2020.<br />
[15]  Y. Shashi, "Deep Learning based Safe Social Distancing and Face 
Mask Detection in Public Areas for COVID -19 Safety Guidelines 
Adherence," International Journal for Research in Applied Science &amp; 
Engineering Technology (IJRASET), 2020.<br />
[16]  J. Mingjie and  X. Fan, RetinaFaceMask: A Face Mask detector, 2020.<br />
[17]  M. S. Ejaz, M. R. Islam, M. Sifatullah and A. Sarker, "Implementation of Principal Component Analysis on Masked and Non -masked Faces 
Recognition," in 1st International Conference on Advances in S cience, 
Engineering and Robotics Technology (ICASERT) , 2019.<br />
[18]  N. U. Din, K. Javed, S. Bae and J. Yi, "A Novel GAN -Based Network 
for Unmasking of Masked Face,”," IEEE Access, vol. 8, p. 44276 –
44287, 2020.<br />
[19]  K. Muhammad, H. Saad, H. Saleet and M . Shahid, "Deep Unified 
Model For Face Recognition Based on Convolution Neural Network 
and Edge Computing," IEEE ACCESS, 2019.<br />
[20]  J. Qi, M. Chong, T. Ling and R. Fankai, "A Region Generation based 
Model for Occluded Face Detection," ELSEVIER, 2019.<br />
[21]  I. Madhura and N. Mehendale, Real-Time Face Mask Identification 
Using Facemasknet Deep Learning Network, 2020.<br />
[22]  S. Xudong, W. Pengcheng and C. H. Steven, "Face detection using 
deep learning: An improved faster RCNN approach," ELSEVIER, 
2018.<br />
[23]  S. Y. Wang, B. Luo and J. Shen, "Face Masks Extraction in Video," 
Springer, 2018.<br />
[24]  D. Chiang, "Detect faces and  determine whether people are wearing 
mask," 2020.<br />
[25]  A. Anwar and A. Raychowdhury, "Masked Face Recognition for 
Secure Authentication," IEEE, 2020.  </p>
<p>Authorized licensed use limited to: George Mason University. Downloaded on March 16,2024 at 16:55:29 UTC from IEEE Xplore.  Restrictions apply. </p>