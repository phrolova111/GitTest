"""CIFAR-10 分类使用的卷积神经网络。"""

from __future__ import annotations

import torch
from torch import nn


class CifarCNN(nn.Module):
    """较小的 CIFAR-10 CNN，适合在 CPU 上训练和评估。"""

    def __init__(self, num_classes: int = 10) -> None:
        super().__init__()

        self.features = nn.Sequential(
            self._conv_block(3, 32),
            self._conv_block(32, 64),
            self._conv_block(64, 128),
        )

        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128 * 4 * 4, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(256, num_classes),
        )

    @staticmethod
    def _conv_block(in_channels: int, out_channels: int) -> nn.Sequential:
        return nn.Sequential(
            nn.Conv2d(
                in_channels,
                out_channels,
                kernel_size=3,
                padding=1,
                bias=False,
            ),
            nn.BatchNorm2d(out_channels),
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
            nn.MaxPool2d(kernel_size=2),
        )

    def forward(self, images: torch.Tensor) -> torch.Tensor:
        features = self.features(images)
        return self.classifier(features)


def build_model(num_classes: int = 10) -> CifarCNN:
    """创建模型，训练和评估程序都通过该函数实例化网络。"""
    return CifarCNN(num_classes=num_classes)

