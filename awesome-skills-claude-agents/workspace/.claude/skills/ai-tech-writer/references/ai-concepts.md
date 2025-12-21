# AI领域核心概念和术语库

## 一、基础概念

### 1. 机器学习基础

| 中文术语 | 英文术语 | 缩写 | 简要说明 |
|---------|---------|-----|---------|
| 人工智能 | Artificial Intelligence | AI | 使计算机模拟人类智能行为的技术 |
| 机器学习 | Machine Learning | ML | 让计算机从数据中自动学习规律的方法 |
| 深度学习 | Deep Learning | DL | 基于多层神经网络的机器学习方法 |
| 神经网络 | Neural Network | NN | 模仿生物神经元结构的计算模型 |
| 监督学习 | Supervised Learning | - | 使用标注数据训练模型 |
| 无监督学习 | Unsupervised Learning | - | 从无标注数据中发现模式 |
| 强化学习 | Reinforcement Learning | RL | 通过与环境交互学习最优策略 |
| 迁移学习 | Transfer Learning | - | 将已学知识应用到新任务 |

### 2. 神经网络架构

| 中文术语 | 英文术语 | 缩写 | 简要说明 |
|---------|---------|-----|---------|
| 卷积神经网络 | Convolutional Neural Network | CNN | 擅长处理图像数据的网络 |
| 循环神经网络 | Recurrent Neural Network | RNN | 擅长处理序列数据的网络 |
| 长短期记忆网络 | Long Short-Term Memory | LSTM | 解决RNN长距离依赖问题的变体 |
| 门控循环单元 | Gated Recurrent Unit | GRU | LSTM的简化版本 |
| 生成对抗网络 | Generative Adversarial Network | GAN | 由生成器和判别器组成的对抗模型 |
| 变分自编码器 | Variational Autoencoder | VAE | 基于概率的生成模型 |
| 图神经网络 | Graph Neural Network | GNN | 处理图结构数据的网络 |

## 二、自然语言处理（NLP）

### 1. 基础概念

| 中文术语 | 英文术语 | 缩写 | 简要说明 |
|---------|---------|-----|---------|
| 自然语言处理 | Natural Language Processing | NLP | 让计算机理解和生成人类语言 |
| 自然语言理解 | Natural Language Understanding | NLU | NLP的子领域，专注理解语义 |
| 自然语言生成 | Natural Language Generation | NLG | 生成流畅自然的文本 |
| 词嵌入 | Word Embedding | - | 将词语映射为向量表示 |
| 分词 | Tokenization | - | 将文本分割为词或子词单元 |
| 命名实体识别 | Named Entity Recognition | NER | 识别文本中的人名、地名等实体 |
| 句法分析 | Syntactic Parsing | - | 分析句子的语法结构 |
| 语义分析 | Semantic Analysis | - | 理解文本的含义 |

### 2. Transformer及相关

| 中文术语 | 英文术语 | 缩写 | 简要说明 |
|---------|---------|-----|---------|
| Transformer | Transformer | - | 基于注意力机制的序列模型架构 |
| 注意力机制 | Attention Mechanism | - | 让模型关注输入的重要部分 |
| 自注意力 | Self-Attention | - | 序列内部元素之间的注意力 |
| 多头注意力 | Multi-Head Attention | - | 并行多个注意力头 |
| 位置编码 | Positional Encoding | PE | 为序列添加位置信息 |
| 编码器 | Encoder | - | 将输入编码为表示 |
| 解码器 | Decoder | - | 从表示生成输出 |
| 交叉注意力 | Cross-Attention | - | 两个序列之间的注意力 |

### 3. 预训练模型

| 中文术语 | 英文术语 | 缩写 | 简要说明 |
|---------|---------|-----|---------|
| 预训练语言模型 | Pre-trained Language Model | PLM | 在大规模语料上预训练的模型 |
| 双向编码器表示 | Bidirectional Encoder Representations from Transformers | BERT | Google的预训练模型 |
| 生成式预训练Transformer | Generative Pre-trained Transformer | GPT | OpenAI的自回归语言模型 |
| 文本到文本迁移Transformer | Text-to-Text Transfer Transformer | T5 | Google的统一文本生成模型 |
| 掩码语言模型 | Masked Language Model | MLM | BERT使用的预训练任务 |
| 因果语言模型 | Causal Language Model | CLM | GPT使用的预训练任务 |

## 三、大语言模型（LLM）

### 1. LLM基础

| 中文术语 | 英文术语 | 缩写 | 简要说明 |
|---------|---------|-----|---------|
| 大语言模型 | Large Language Model | LLM | 参数规模巨大的语言模型 |
| 基座模型 | Foundation Model | - | 在大规模数据上训练的通用模型 |
| 提示词 | Prompt | - | 引导模型生成的输入文本 |
| 提示工程 | Prompt Engineering | - | 设计有效提示词的技术 |
| 上下文学习 | In-Context Learning | ICL | 通过示例在提示中学习 |
| 少样本学习 | Few-Shot Learning | - | 使用少量示例进行学习 |
| 零样本学习 | Zero-Shot Learning | - | 无需示例直接执行任务 |
| 思维链 | Chain-of-Thought | CoT | 引导模型逐步推理 |

### 2. 模型训练与优化

| 中文术语 | 英文术语 | 缩写 | 简要说明 |
|---------|---------|-----|---------|
| 微调 | Fine-Tuning | FT | 在特定任务上调整预训练模型 |
| 指令微调 | Instruction Tuning | - | 使用指令数据微调模型 |
| 人类反馈强化学习 | Reinforcement Learning from Human Feedback | RLHF | 使用人类偏好优化模型 |
| 参数高效微调 | Parameter-Efficient Fine-Tuning | PEFT | 只调整部分参数的微调方法 |
| 低秩适应 | Low-Rank Adaptation | LoRA | 通过低秩矩阵进行参数高效微调 |
| 适配器 | Adapter | - | 在预训练模型中插入的可训练模块 |
| 前缀微调 | Prefix Tuning | - | 添加可训练的前缀向量 |
| 提示微调 | Prompt Tuning | - | 只训练连续的提示向量 |

### 3. 推理优化

| 中文术语 | 英文术语 | 缩写 | 简要说明 |
|---------|---------|-----|---------|
| 量化 | Quantization | - | 降低模型权重的精度 |
| 剪枝 | Pruning | - | 移除不重要的模型参数 |
| 知识蒸馏 | Knowledge Distillation | KD | 用大模型训练小模型 |
| 键值缓存 | Key-Value Cache | KV Cache | 缓存注意力计算结果 |
| 批处理 | Batching | - | 同时处理多个请求 |
| 流式生成 | Streaming | - | 逐token生成输出 |
| 投机解码 | Speculative Decoding | - | 使用小模型加速生成 |

## 四、检索增强生成（RAG）

### RAG核心概念

| 中文术语 | 英文术语 | 缩写 | 简要说明 |
|---------|---------|-----|---------|
| 检索增强生成 | Retrieval-Augmented Generation | RAG | 结合检索和生成的方法 |
| 向量数据库 | Vector Database | - | 存储和检索向量的数据库 |
| 向量嵌入 | Vector Embedding | - | 将文本转换为向量表示 |
| 语义检索 | Semantic Retrieval | - | 基于语义相似度的检索 |
| 文档分块 | Document Chunking | - | 将长文档分割为小块 |
| 余弦相似度 | Cosine Similarity | - | 衡量向量相似度的指标 |
| 密集检索 | Dense Retrieval | - | 基于稠密向量的检索 |
| 混合检索 | Hybrid Retrieval | - | 结合多种检索方法 |

## 五、AI Agent

### 1. Agent基础

| 中文术语 | 英文术语 | 缩写 | 简要说明 |
|---------|---------|-----|---------|
| AI智能体 | AI Agent | - | 能自主感知和行动的AI系统 |
| 工具调用 | Tool Calling | - | Agent调用外部工具的能力 |
| 函数调用 | Function Calling | - | 模型调用预定义函数 |
| 多智能体系统 | Multi-Agent System | MAS | 多个Agent协作的系统 |
| 智能体框架 | Agent Framework | - | 构建Agent的软件框架 |
| 推理循环 | Reasoning Loop | - | Agent的思考-行动循环 |
| 规划 | Planning | - | 制定行动计划的能力 |
| 记忆 | Memory | - | Agent的短期/长期记忆 |

### 2. Agent设计模式

| 中文术语 | 英文术语 | 缩写 | 简要说明 |
|---------|---------|-----|---------|
| 反思 | Reflection | - | Agent自我评估和改进 |
| 工具使用 | Tool Use | - | 调用外部工具完成任务 |
| 多步推理 | Multi-Step Reasoning | - | 分解复杂任务逐步执行 |
| 自我一致性 | Self-Consistency | - | 通过多次采样提高准确性 |
| 树状搜索 | Tree-of-Thought | ToT | 探索多条推理路径 |

## 六、计算机视觉（CV）

### CV核心概念

| 中文术语 | 英文术语 | 缩写 | 简要说明 |
|---------|---------|-----|---------|
| 计算机视觉 | Computer Vision | CV | 让计算机理解图像和视频 |
| 图像分类 | Image Classification | - | 识别图像所属类别 |
| 目标检测 | Object Detection | - | 定位和识别图像中的对象 |
| 图像分割 | Image Segmentation | - | 将图像分割为多个区域 |
| 实例分割 | Instance Segmentation | - | 区分同类对象的不同实例 |
| 语义分割 | Semantic Segmentation | - | 为每个像素分配类别 |
| 姿态估计 | Pose Estimation | - | 检测人体关键点位置 |
| 视觉Transformer | Vision Transformer | ViT | 将Transformer应用于视觉任务 |

## 七、多模态AI

### 多模态核心概念

| 中文术语 | 英文术语 | 缩写 | 简要说明 |
|---------|---------|-----|---------|
| 多模态学习 | Multimodal Learning | - | 处理多种数据类型的学习 |
| 视觉语言模型 | Vision-Language Model | VLM | 理解图像和文本的模型 |
| 图文对比学习 | Contrastive Language-Image Pre-training | CLIP | OpenAI的图文匹配模型 |
| 文本到图像生成 | Text-to-Image Generation | T2I | 根据文本生成图像 |
| 图像到文本生成 | Image-to-Text Generation | I2T | 根据图像生成描述 |
| 扩散模型 | Diffusion Model | - | 通过去噪过程生成图像 |
| 稳定扩散 | Stable Diffusion | SD | 开源的文本到图像模型 |

## 八、模型评估与基准

### 评估指标

| 中文术语 | 英文术语 | 缩写 | 简要说明 |
|---------|---------|-----|---------|
| 困惑度 | Perplexity | PPL | 衡量语言模型的不确定性 |
| BLEU分数 | BLEU Score | BLEU | 机器翻译质量评估 |
| ROUGE分数 | ROUGE Score | ROUGE | 文本摘要质量评估 |
| F1分数 | F1 Score | F1 | 精确率和召回率的调和平均 |
| 准确率 | Accuracy | - | 预测正确的比例 |
| 召回率 | Recall | - | 正样本被正确识别的比例 |
| 精确率 | Precision | - | 预测为正的样本中真正为正的比例 |

### 主流基准测试

| 英文名称 | 全称 | 简要说明 |
|---------|-----|---------|
| MMLU | Massive Multitask Language Understanding | 大规模多任务语言理解 |
| HellaSwag | - | 常识推理基准 |
| HumanEval | - | 代码生成能力评估 |
| GSM8K | Grade School Math 8K | 小学数学问题求解 |
| TruthfulQA | - | 真实性和可信度评估 |
| BBH | Big-Bench Hard | 困难任务集合 |
| GLUE | General Language Understanding Evaluation | 通用语言理解评估 |
| SuperGLUE | - | 更难的GLUE版本 |

## 九、训练技术

### 训练方法

| 中文术语 | 英文术语 | 缩写 | 简要说明 |
|---------|---------|-----|---------|
| 反向传播 | Backpropagation | - | 计算梯度的算法 |
| 梯度下降 | Gradient Descent | GD | 优化算法基础 |
| 随机梯度下降 | Stochastic Gradient Descent | SGD | 使用随机样本的梯度下降 |
| Adam优化器 | Adaptive Moment Estimation | Adam | 自适应学习率优化器 |
| 学习率调度 | Learning Rate Scheduling | - | 动态调整学习率 |
| 批归一化 | Batch Normalization | BN | 标准化批次数据 |
| 层归一化 | Layer Normalization | LN | 标准化层输出 |
| Dropout | Dropout | - | 随机丢弃神经元防止过拟合 |
| 梯度裁剪 | Gradient Clipping | - | 限制梯度大小防止爆炸 |
| 混合精度训练 | Mixed Precision Training | - | 使用FP16和FP32混合训练 |

### 分布式训练

| 中文术语 | 英文术语 | 缩写 | 简要说明 |
|---------|---------|-----|---------|
| 数据并行 | Data Parallelism | DP | 在多个设备上复制模型 |
| 模型并行 | Model Parallelism | MP | 将模型分割到多个设备 |
| 流水线并行 | Pipeline Parallelism | PP | 按层分割模型形成流水线 |
| 张量并行 | Tensor Parallelism | TP | 分割张量到多个设备 |
| ZeRO优化 | Zero Redundancy Optimizer | ZeRO | 减少内存冗余的优化技术 |
| 梯度累积 | Gradient Accumulation | - | 累积多个批次的梯度 |
| 梯度检查点 | Gradient Checkpointing | - | 重新计算中间激活值节省内存 |

## 十、实用技巧和最佳实践

### 常见技术搭配

#### NLP任务技术栈
- **文本分类**：BERT + 分类头 / Sentence Transformers
- **文本生成**：GPT系列 / T5 / BART
- **问答系统**：RAG架构 + Vector DB + LLM
- **对话系统**：ChatGPT / Claude + Prompt Engineering
- **信息抽取**：BERT-based NER + Relation Extraction

#### CV任务技术栈
- **图像分类**：ResNet / EfficientNet / ViT
- **目标检测**：YOLO / Faster R-CNN / DETR
- **图像分割**：U-Net / Mask R-CNN / Segment Anything
- **图像生成**：Stable Diffusion / DALL-E / Midjourney

#### Agent任务技术栈
- **简单Agent**：LLM + Function Calling
- **复杂Agent**：LangChain / AutoGPT + Tool Use
- **多Agent协作**：Agent2Agent / Multi-Agent Framework

### 术语使用建议

#### 优先使用英文的术语（专业性强）
- Transformer, Attention, Embedding
- Fine-tuning, Prompt, Token
- RAG, LoRA, RLHF
- API, GPU, TPU

#### 可使用中文的术语（通用概念）
- 神经网络、深度学习、机器学习
- 训练、推理、部署
- 准确率、召回率、F1分数
- 数据集、模型、算法

#### 需要中英对照的术语（首次出现）
- 检索增强生成（RAG）
- 低秩适应（LoRA）
- 人类反馈强化学习（RLHF）
- 参数高效微调（PEFT）
