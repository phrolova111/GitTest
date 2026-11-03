"""CIFAR-10 分类使用的卷积神经网络。"""

from __future__ import annotations

import torch              #导入PyTorch库
from torch import nn      #从 torch 里导入 nn 子模块（torch.nn）


class CifarCNN(nn.Module):         #定义一个类，继承自 nn.Module，表示一个卷积神经网络模型
    """较小的 CIFAR-10 CNN，适合在 CPU 上训练和评估。"""

    def __init__(self, num_classes: int = 10) -> None:    #构造函数，10个类别数，无返回值
        super().__init__()                                #先调用父类nn.Module

        self.features = nn.Sequential(       #三个卷积块，每个卷积块包含两个卷积层
            self._conv_block(3, 32),         #输入3个通道，输出32个通道
            self._conv_block(32, 64),
            self._conv_block(64, 128),
        )

        self.classifier = nn.Sequential(    #把features输出的4D特征图变成类别logits
            nn.Flatten(),
            nn.Linear(128 * 4 * 4, 256),    #隐藏层，输入128*4*4=2048个特征，输出256个特征
            nn.ReLU(inplace=True),          #激活函数ReLU，inplace=True表示直接在输入上进行修改，节省内存
            nn.Dropout(0.5),                #0.5的概率，防止过拟合
            nn.Linear(256, num_classes),    #输出层
        )

#    _conv_block 静态方法
    @staticmethod
    def _conv_block(in_channels: int, out_channels: int) -> nn.Sequential:
    #输入输出通道数， 返回一个 nn.Sequential   
        return nn.Sequential(
            nn.Conv2d(
                in_channels,
                out_channels,
                kernel_size=3,      #3*3的卷积核
                padding=1,
                bias=False,         #不加偏置，减少参考数，避免无意义更新
            ),
            nn.BatchNorm2d(out_channels),    #BN放在激活前，让进入ReLU的值分布稳定在0附近，避免大量神经元死亡
            nn.ReLU(inplace=True),
            nn.Conv2d(
                out_channels,
                out_channels,
                kernel_size=3,
                padding=1,
                bias=False,
            ),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2),    #2*2的最大池化层，减半特征图尺寸
        )

    def forward(self, images: torch.Tensor) -> torch.Tensor:
        features = self.features(images)
        return self.classifier(features)


def build_model(num_classes: int = 10) -> CifarCNN:
    """创建模型，训练和评估程序都通过该函数实例化网络。"""
    return CifarCNN(num_classes=num_classes)