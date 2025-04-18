import torch
import torch.nn as nn
import torch.nn.functional as F

# Base ResNet20 class for CIFAR-10
# General class being kept in a separate file if needed in any sparsity method

class ResBlock(nn.Module):
    def __init__(self, in_chan, out_chan, stride):
        super(ResBlock, self).__init__()
        self.conv1 = nn.Conv2d(in_channels=in_chan, out_channels=out_chan, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bnorm1 = nn.BatchNorm2d(out_chan)
        self.conv2 = nn.Conv2d(in_channels=out_chan, out_channels=out_chan, kernel_size=3, stride=1, padding=1, bias=False)
        self.bnorm2 = nn.BatchNorm2d(out_chan)
        
        self.residual = nn.Sequential()
        if stride != 1 or in_chan != out_chan: # Convolution of kernel size of 1 if number of output filters changes
            self.residual = nn.Sequential(
                nn.Conv2d(in_chan, out_chan, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(out_chan)
            )
    
    def forward(self, x):
        identity = self.residual(x)
        x = torch.relu(self.bnorm1(self.conv1(x)))
        x = self.bnorm2(self.conv2(x))
        x += identity
        return torch.relu(x)


class ResNet20(nn.Module):
    def __init__(self):
        super(ResNet20, self).__init__()
        self.in_chan = 16
        
        self.conv1 = nn.Conv2d(in_channels=3, out_channels=16, kernel_size=3, stride=1, padding=1, bias=False)
        self.bnorm1 = nn.BatchNorm2d(16)

        self.residual_layers = nn.Sequential(
            ResBlock(16, 16, stride=1), ResBlock(16, 16, stride=1), ResBlock(16, 16, stride=1),

            ResBlock(16, 32, stride=2), ResBlock(32, 32, stride=1), ResBlock(32, 32, stride=1),

            ResBlock(32, 64, stride=2), ResBlock(64, 64, stride=1), ResBlock(64, 64, stride=1),
        )

        self.pool = nn.AvgPool2d(8)
        self.classifier = nn.Linear(64, 10) # 10-digit CIFAR-10 classification
    
    def forward(self, x):
        x = torch.relu(self.bnorm1(self.conv1(x)))  
        x = self.residual_layers(x)
        x = self.pool(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x


# _AFFINE = True

# class LambdaLayer(nn.Module):
#     def __init__(self, lambd):
#         super(LambdaLayer, self).__init__()
#         self.lambd = lambd

#     def forward(self, x):
#         return self.lambd(x)


# class BasicBlock(nn.Module):
#     expansion = 1

#     def __init__(self, in_planes, planes, stride=1):
#         super(BasicBlock, self).__init__()
#         self.conv1 = nn.Conv2d(in_planes, planes, kernel_size=3, stride=stride, padding=1, bias=False)
#         self.bn1 = nn.BatchNorm2d(planes, affine=_AFFINE)
#         self.conv2 = nn.Conv2d(planes, planes, kernel_size=3, stride=1, padding=1, bias=False)
#         self.bn2 = nn.BatchNorm2d(planes, affine=_AFFINE)

#         self.downsample = None
#         self.bn3 = None
#         if stride != 1 or in_planes != planes:
#             self.downsample = nn.Sequential(
#                 nn.Conv2d(in_planes, self.expansion * planes, kernel_size=1, stride=stride, bias=False))
#             self.bn3 = nn.BatchNorm2d(self.expansion * planes, affine=_AFFINE)

#     def forward(self, x):
#         # x: batch_size * in_c * h * w
#         residual = x
#         out = F.relu(self.bn1(self.conv1(x)))
#         out = self.bn2(self.conv2(out))
#         if self.downsample is not None:
#             residual = self.bn3(self.downsample(x))
#         out += residual
#         out = F.relu(out)
#         return out


# class ResNet(nn.Module):
#     def __init__(self, block, num_blocks, num_classes=10):
#         super(ResNet, self).__init__()
#         _outputs = [32, 64, 128]
#         self.in_planes = _outputs[0]

#         self.conv1 = nn.Conv2d(3, _outputs[0], kernel_size=3, stride=1, padding=1, bias=False)
#         self.bn = nn.BatchNorm2d(_outputs[0], affine=_AFFINE)
#         self.layer1 = self._make_layer(block, _outputs[0], num_blocks[0], stride=1)
#         self.layer2 = self._make_layer(block, _outputs[1], num_blocks[1], stride=2)
#         self.layer3 = self._make_layer(block, _outputs[2], num_blocks[2], stride=2)
#         self.linear = nn.Linear(_outputs[2], num_classes)

#         self.apply(weights_init)

#     def _make_layer(self, block, planes, num_blocks, stride):
#         strides = [stride] + [1]*(num_blocks-1)
#         layers = []
#         for stride in strides:
#             layers.append(block(self.in_planes, planes, stride))
#             self.in_planes = planes * block.expansion

#         return nn.Sequential(*layers)

#     def forward(self, x):
#         out = F.relu(self.bn(self.conv1(x)))
#         out = self.layer1(out)
#         out = self.layer2(out)
#         out = self.layer3(out)
#         out = F.avg_pool2d(out, out.size()[3])
#         out = out.view(out.size(0), -1)
#         out = self.linear(out)
#         return out


# def resnet(depth=32, num_classes=100):
#     assert (depth - 2) % 6 == 0, 'Depth must be = 6n + 2, got %d' % depth
#     n = (depth - 2) // 6
#     return ResNet(BasicBlock, [n]*3, num_classes)