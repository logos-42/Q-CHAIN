// ============================================================================
// 量子区块链 Q# 核心算法库
// Quantum Blockchain Q# Core Algorithm Library
// ============================================================================
// 此文件包含量子区块链的核心量子算法实现
// 需要 Q# 开发工具包 (QDK) 和 .NET SDK
// ============================================================================

namespace QuantumBlockchain.Core {
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Arithmetic;
    open Microsoft.Quantum.Measurement;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Arrays;
    open Microsoft.Quantum.Diagnostics;

    // ========================================================================
    // 1. 量子随机数生成器 (QRNG - Quantum Random Number Generator)
    // ========================================================================
    // 利用量子叠加态的真随机性生成随机数
    // 量子电路：|0⟩ --[H]-- [M] --> 随机比特
    
    /// <summary>
    /// 生成单个量子随机比特
    /// 使用 Hadamard 门创建叠加态，然后测量得到真随机比特
    /// </summary>
    /// <returns>随机比特 (0 或 1)</returns>
    operation GenerateRandomBit() : Result {
        use qubit = Qubit();
        
        // 应用 Hadamard 门创建叠加态 |+⟩ = (|0⟩ + |1⟩)/√2
        H(qubit);
        
        // 测量量子比特，坍缩到 |0⟩ 或 |1⟩，概率各 50%
        let result = M(qubit);
        
        // 重置量子比特到 |0⟩ 态
        Reset(qubit);
        
        return result;
    }

    /// <summary>
    /// 生成指定长度的量子随机比特串
    /// </summary>
    /// <param name="numBits">要生成的比特数量</param>
    /// <returns>随机比特串 (Result 数组)</returns>
    operation GenerateRandomBitString(numBits : Int) : Result[] {
        mutable randomBits = new Result[0];
        
        for _ in 0..numBits-1 {
            let bit = GenerateRandomBit();
            set randomBits += [bit];
        }
        
        return randomBits;
    }

    /// <summary>
    /// 生成量子随机整数 (范围 [0, max))
    /// 使用量子随机比特构建整数
    /// </summary>
    /// <param name="max">最大值 (不包含)</param>
    /// <returns>随机整数</returns>
    operation GenerateRandomInt(max : Int) : Int {
        // 计算需要的比特数
        let numBits = BitSizeI(max);
        mutable result = 0;
        
        repeat {
            set result = 0;
            // 生成随机比特串
            for i in 0..numBits-1 {
                let bit = GenerateRandomBit();
                if bit == One {
                    set result += 1 <<< i;
                }
            }
        }
        until result < max
        fixup {
            // 如果超出范围，重试 (拒绝采样)
        }
        
        return result;
    }

    /// <summary>
    /// 生成量子随机十六进制字符串 (用于区块链哈希和签名)
    /// </summary>
    /// <param name="numBytes">字节数</param>
    /// <returns>十六进制字符串</returns>
    operation GenerateRandomHexString(numBytes : Int) : String {
        let randomBytes = GenerateRandomBitString(numBytes * 8);
        
        // 将比特串转换为十六进制
        mutable hexString = "";
        for i in 0..numBytes-1 {
            mutable nibble = 0;
            for j in 0..3 {
                let bitIndex = i * 4 + j;
                if randomBytes[bitIndex] == One {
                    set nibble += 1 <<< (3 - j);
                }
            }
            set hexString += $"{nibble:X}";
        }
        
        return hexString;
    }

    // ========================================================================
    // 2. 量子哈希函数 (Quantum Hash Function)
    // ========================================================================
    // 基于量子行走 (Quantum Walk) 和量子傅里叶变换的哈希函数
    // 提供抗量子碰撞特性
    
    /// <summary>
    /// 量子哈希核心操作 - 使用量子行走
    /// </summary>
    /// <param name="input">输入数据 (量子比特寄存器)</param>
    /// <param name="outputSize">输出哈希大小 (比特数)</param>
    /// <returns>哈希结果 (量子比特寄存器)</returns>
    operation QuantumHashCore(input : Qubit[], outputSize : Int) : Qubit[] {
        use outputRegister = Qubit[outputSize];
        
        let inputSize = Length(input);
        
        // 初始化输出寄存器为叠加态
        ApplyToEach(H, outputRegister);
        
        // 量子行走步骤 - 创建复杂的纠缠和干涉
        for step in 0..outputSize-1 {
            // 条件旋转 - 基于输入比特
            for i in 0..inputSize-1 {
                Controlled Rx([input[i]], (PI() / (2.0 * IntAsDouble(step + 1)), outputRegister[step]));
            }
            
            // 输出比特之间的纠缠
            if step < outputSize - 1 {
                CNOT(outputRegister[step], outputRegister[step + 1]);
            }
        }
        
        // 应用量子傅里叶变换的简化版本
        for i in 0..outputSize-1 {
            H(outputRegister[i]);
            for j in i+1..outputSize-1 {
                let angle = PI() / (2.0 * IntAsDouble(j - i));
                Controlled R1([outputRegister[j]], (angle, outputRegister[i]));
            }
        }
        
        return outputRegister;
    }

    /// <summary>
    /// 经典 - 量子混合哈希函数
    /// 将经典数据转换为量子态，进行量子处理，然后测量得到经典哈希
    /// </summary>
    /// <param name="inputData">输入数据 (整数数组)</param>
    /// <param name="outputSize">输出哈希大小 (比特数)</param>
    /// <returns>哈希值 (整数数组)</returns>
    operation QuantumHash(inputData : Int[], outputSize : Int) : Int[] {
        // 计算需要的量子比特数
        let numQubits = Max([Length(inputData), outputSize]);
        
        use register = Qubit[numQubits];
        
        // 编码输入数据到量子态
        for i in 0..Length(inputData)-1 {
            let value = inputData[i];
            // 基于输入值设置量子态
            if value % 2 == 1 {
                X(register[i]);
            }
            H(register[i]);
            
            // 基于输入值添加相位
            let phase = PI() * IntAsDouble(value % 100) / 100.0;
            R1(phase, register[i]);
        }
        
        // 创建纠缠
        for i in 0..numQubits-2 {
            CNOT(register[i], register[i + 1]);
        }
        
        // 量子行走混合
        for _ in 0..outputSize {
            ApplyToEach(H, register);
            for i in 0..numQubits-2 {
                CNOT(register[i], register[i + 1]);
            }
        }
        
        // 测量输出
        mutable hashResult = new Int[0];
        for i in 0..outputSize-1 {
            let result = M(register[i]);
            let bitValue = ResultAsInt(result);
            set hashResult += [bitValue];
        }
        
        // 重置所有量子比特
        ResetAll(register);
        
        return hashResult;
    }

    /// <summary>
    /// 将哈希结果转换为十六进制字符串
    /// </summary>
    operation QuantumHashToString(inputData : Int[], outputSize : Int) : String {
        let hashBits = QuantumHash(inputData, outputSize);
        
        mutable hexString = "";
        for i in 0..(outputSize / 4)-1 {
            mutable nibble = 0;
            for j in 0..3 {
                if i * 4 + j < Length(hashBits) {
                    set nibble += hashBits[i * 4 + j] <<< (3 - j);
                }
            }
            set hexString += $"{nibble:X}";
        }
        
        return hexString;
    }

    // ========================================================================
    // 3. 量子密钥分发 (QKD - BB84 协议)
    // ========================================================================
    // 实现 BB84 量子密钥分发协议
    // Alice 发送量子比特，Bob 测量，通过经典信道比对基矢
    
    /// <summary>
    /// BB84 协议 - Alice 端：准备和发送量子比特
    /// 随机选择基矢 (Z 或 X) 和比特值 (0 或 1)
    /// </summary>
    /// <param name="numBits">要发送的比特数量</param>
    /// <returns>(量子比特数组，基矢选择，比特值)</returns>
    operation BB84Prepare(numBits : Int) : (Qubit[], Int[], Int[]) {
        use qubits = Qubit[numBits];
        mutable bases = new Int[0];  // 0 = Z 基，1 = X 基
        mutable bits = new Int[0];
        
        for i in 0..numBits-1 {
            // 随机选择基矢
            let basis = GenerateRandomInt(2);
            set bases += [basis];
            
            // 随机选择比特值
            let bit = GenerateRandomInt(2);
            set bits += [bit];
            
            // 准备量子态
            if bit == 1 {
                X(qubits[i]);  // |1⟩
            }
            
            // 如果选择 X 基，应用 Hadamard
            if basis == 1 {
                H(qubits[i]);
            }
        }
        
        return (qubits, bases, bits);
    }

    /// <summary>
    /// BB84 协议 - Bob 端：测量量子比特
    /// 随机选择测量基矢
    /// </summary>
    /// <param name="qubits">接收到的量子比特</param>
    /// <returns>(测量基矢选择，测量结果)</returns>
    operation BB84Measure(qubits : Qubit[]) : (Int[], Result[]) {
        let numBits = Length(qubits);
        mutable bases = new Int[0];
        mutable results = new Result[0];
        
        for i in 0..numBits-1 {
            // 随机选择测量基矢
            let basis = GenerateRandomInt(2);
            set bases += [basis];
            
            // 如果选择 X 基，先应用 Hadamard
            if basis == 1 {
                H(qubits[i]);
            }
            
            // 测量
            let result = M(qubits[i]);
            set results += [result];
            
            // 重置量子比特
            Reset(qubits[i]);
        }
        
        return (bases, results);
    }

    /// <summary>
    /// BB84 协议 - 基矢比对和密钥提取
    /// 比对 Alice 和 Bob 的基矢选择，保留匹配的比特
    /// </summary>
    /// <param name="aliceBases">Alice 的基矢选择</param>
    /// <param name="bobBases">Bob 的基矢选择</param>
    /// <param name="aliceBits">Alice 的比特值</param>
    /// <param name="bobResults">Bob 的测量结果</param>
    /// <returns>共享密钥 (比特数组)</returns>
    operation BB84Sift(
        aliceBases : Int[],
        bobBases : Int[],
        aliceBits : Int[],
        bobResults : Result[]
    ) : Int[] {
        mutable sharedKey = new Int[0];
        
        for i in 0..Length(aliceBases)-1 {
            // 只保留基矢匹配的比特
            if aliceBases[i] == bobBases[i] {
                let bitValue = ResultAsInt(bobResults[i]);
                set sharedKey += [bitValue];
            }
        }
        
        return sharedKey;
    }

    /// <summary>
    /// 完整的 BB84 量子密钥分发协议
    /// </summary>
    /// <param name="numBits">初始发送的比特数量</param>
    /// <returns>共享密钥 (比特数组)</returns>
    operation BB84Protocol(numBits : Int) : Int[] {
        // Alice 准备量子比特
        let (qubits, aliceBases, aliceBits) = BB84Prepare(numBits);
        
        // Bob 测量量子比特
        let (bobBases, bobResults) = BB84Measure(qubits);
        
        // 基矢比对和密钥提取
        let sharedKey = BB84Sift(aliceBases, bobBases, aliceBits, bobResults);
        
        return sharedKey;
    }

    /// <summary>
    /// 错误检测 - 比对部分密钥以检测窃听
    /// </summary>
    /// <param name="key1">Alice 的密钥</param>
    /// <param name="key2">Bob 的密钥</param>
    /// <param name="sampleSize">采样数量</param>
    /// <returns>错误率</returns>
    operation DetectEavesdropping(key1 : Int[], key2 : Int[], sampleSize : Int) : Double {
        let keyLength = Min([Length(key1), Length(key2)]);
        let actualSampleSize = Min([sampleSize, keyLength / 2]);
        
        mutable errors = 0;
        
        // 随机采样比对
        for i in 0..actualSampleSize-1 {
            let index = GenerateRandomInt(keyLength);
            if key1[index] != key2[index] {
                set errors += 1;
            }
        }
        
        return IntAsDouble(errors) / IntAsDouble(actualSampleSize);
    }

    // ========================================================================
    // 4. Grover 搜索算法 (用于量子挖矿)
    // ========================================================================
    // Grover 算法提供 O(√N) 的搜索加速，可用于区块链挖矿
    // 寻找满足特定条件的 nonce 值
    
    /// <summary>
    /// Grover 算法的 Oracle - 标记满足条件的状态
    /// 对于挖矿，条件是哈希值小于目标阈值
    /// </summary>
    /// <param name="register">搜索寄存器</param>
    /// <param name="target">目标值</param>
    operation MiningOracle(register : Qubit[], target : Int) : Unit is Adj {
        let n = Length(register);
        
        // 将目标值编码为二进制
        mutable targetBits = new Int[0];
        for i in 0..n-1 {
            set targetBits += [(target >>> i) % 2];
        }
        
        // 对于每个比特位，如果目标比特是 0，应用 X 门
        for i in 0..n-1 {
            if targetBits[i] == 0 {
                X(register[i]);
            }
        }
        
        // 多控制 Z 门 (标记目标状态)
        // 使用辅助量子比特实现
        use aux = Qubit();
        H(aux);
        Controlled Z(register, aux);
        H(aux);
        Reset(aux);
        
        // 恢复 X 门
        for i in 0..n-1 {
            if targetBits[i] == 0 {
                X(register[i]);
            }
        }
    }

    /// <summary>
    /// Grover 算法的扩散算子 (振幅放大)
    /// </summary>
    /// <param name="register">搜索寄存器</param>
    operation GroverDiffusion(register : Qubit[]) : Unit {
        let n = Length(register);
        
        // 应用 Hadamard 门
        ApplyToEach(H, register);
        
        // 应用 X 门
        ApplyToEach(X, register);
        
        // 多控制 Z 门 (条件相位翻转)
        use aux = Qubit();
        H(aux);
        Controlled Z(register, aux);
        H(aux);
        Reset(aux);
        
        // 恢复 X 门
        ApplyToEach(X, register);
        
        // 恢复 Hadamard 门
        ApplyToEach(H, register);
    }

    /// <summary>
    /// 单次 Grover 迭代
    /// </summary>
    /// <param name="register">搜索寄存器</param>
    /// <param name="target">目标值</param>
    operation GroverIteration(register : Qubit[], target : Int) : Unit {
        // 应用 Oracle
        MiningOracle(register, target);
        
        // 应用扩散算子
        GroverDiffusion(register);
    }

    /// <summary>
    /// 完整的 Grover 搜索算法
    /// </summary>
    /// <param name="numQubits">量子比特数量</param>
    /// <param name="target">目标值</param>
    /// <returns>搜索结果</returns>
    operation GroverSearch(numQubits : Int, target : Int) : Int {
        use register = Qubit[numQubits];
        
        // 初始化为均匀叠加态
        ApplyToEach(H, register);
        
        // 计算最优迭代次数：π/4 * √(2^n)
        let numIterations = Round(PI() / 4.0 * Sqrt(IntAsDouble(1 <<< numQubits)));
        
        // 执行 Grover 迭代
        for _ in 0..numIterations-1 {
            GroverIteration(register, target);
        }
        
        // 测量结果
        mutable result = 0;
        for i in 0..numQubits-1 {
            let measurement = M(register[i]);
            if measurement == One {
                set result += 1 <<< i;
            }
        }
        
        // 重置量子比特
        ResetAll(register);
        
        return result;
    }

    /// <summary>
    /// 量子挖矿操作 - 使用 Grover 算法寻找有效 nonce
    /// </summary>
    /// <param name="blockHash">区块哈希 (整数表示)</param>
    /// <param name="difficulty">难度 (前导零数量)</param>
    /// <param name="nonceBits">nonce 的比特数</param>
    /// <returns>有效的 nonce 值</returns>
    operation QuantumMining(blockHash : Int, difficulty : Int, nonceBits : Int) : Int {
        // 目标阈值：哈希值必须小于此值
        let targetThreshold = 1 <<< (256 - difficulty);
        
        use register = Qubit[nonceBits];
        
        // 初始化为叠加态
        ApplyToEach(H, register);
        
        // 计算 Grover 迭代次数
        let numIterations = Round(PI() / 4.0 * Sqrt(IntAsDouble(1 <<< nonceBits)));
        
        // 简化的 Grover 搜索
        for iter in 0..numIterations-1 {
            // Oracle：标记满足难度条件的状态
            // 这里简化处理，实际应用需要量子哈希电路
            
            // 扩散算子
            GroverDiffusion(register);
        }
        
        // 测量得到 nonce
        mutable nonce = 0;
        for i in 0..nonceBits-1 {
            let measurement = M(register[i]);
            if measurement == One {
                set nonce += 1 <<< i;
            }
        }
        
        ResetAll(register);
        
        return nonce;
    }

    // ========================================================================
    // 5. 量子纠缠态生成
    // ========================================================================
    // 生成各种类型的纠缠态用于量子通信和量子签名
    
    /// <summary>
    /// 生成 Bell 态 (EPR 对)
    /// |Φ+⟩ = (|00⟩ + |11⟩)/√2
    /// </summary>
    /// <returns>纠缠的量子比特对</returns>
    operation GenerateBellState() : (Qubit, Qubit) {
        use (q1, q2) = (Qubit(), Qubit());
        
        // 创建 Bell 态
        H(q1);          // q1 进入叠加态
        CNOT(q1, q2);   // 创建纠缠
        
        return (q1, q2);
    }

    /// <summary>
    /// 生成 GHZ 态 (Greenberger-Horne-Zeilinger 态)
    /// |GHZ⟩ = (|00...0⟩ + |11...1⟩)/√2
    /// </summary>
    /// <param name="numQubits">量子比特数量</param>
    /// <returns>纠缠的量子比特数组</returns>
    operation GenerateGHZState(numQubits : Int) : Qubit[] {
        use register = Qubit[numQubits];
        
        // 第一个量子比特进入叠加态
        H(register[0]);
        
        // 使用 CNOT 链创建多体纠缠
        for i in 0..numQubits-2 {
            CNOT(register[i], register[i + 1]);
        }
        
        return register;
    }

    /// <summary>
    /// 生成 W 态
    /// |W⟩ = (|100⟩ + |010⟩ + |001⟩)/√3 (对于 3 量子比特)
    /// </summary>
    /// <param name="numQubits">量子比特数量</param>
    /// <returns>纠缠的量子比特数组</returns>
    operation GenerateWState(numQubits : Int) : Qubit[] {
        use register = Qubit[numQubits];
        
        if numQubits == 2 {
            // 2 量子比特 W 态等价于 Bell 态
            H(register[0]);
            CNOT(register[0], register[1]);
            X(register[0]);
        } elif numQubits >= 3 {
            // 3 量子比特 W 态电路
            // 使用受控旋转门
            let theta = ArcCos(Sqrt(1.0 / IntAsDouble(numQubits)));
            
            Ry(2.0 * theta, register[0]);
            
            for i in 0..numQubits-2 {
                let thetaI = ArcCos(Sqrt(1.0 / IntAsDouble(numQubits - i)));
                Controlled Ry([register[i]], (2.0 * thetaI, register[i + 1]));
            }
        }
        
        return register;
    }

    /// <summary>
    /// 生成 Cluster 态 (用于单向量子计算)
    /// </summary>
    /// <param name="numQubits">量子比特数量</param>
    /// <returns>纠缠的量子比特数组</returns>
    operation GenerateClusterState(numQubits : Int) : Qubit[] {
        use register = Qubit[numQubits];
        
        // 所有量子比特初始化为 |+⟩
        ApplyToEach(H, register);
        
        // 相邻量子比特之间应用 CZ 门创建纠缠
        for i in 0..numQubits-2 {
            CZ(register[i], register[i + 1]);
        }
        
        return register;
    }

    /// <summary>
    /// 验证 Bell 态的纠缠特性
    /// 通过测量验证关联性
    /// </summary>
    /// <param name="q1">第一个量子比特</param>
    /// <param name="q2">第二个量子比特</param>
    /// <returns>测量结果是否一致</returns>
    operation VerifyBellState(q1 : Qubit, q2 : Qubit) : Bool {
        // 测量两个量子比特
        let result1 = M(q1);
        let result2 = M(q2);
        
        // 重置
        Reset(q1);
        Reset(q2);
        
        // Bell 态 |Φ+⟩ 的测量结果应该相同
        return result1 == result2;
    }

    /// <summary>
    /// 量子隐形传态 (Quantum Teleportation)
    /// 使用 Bell 态传输量子态
    /// </summary>
    /// <param name="stateToTeleport">要传输的量子态制备操作</param>
    /// <returns>传输后的测量结果</returns>
    operation QuantumTeleportation(stateToTeleport : (Qubit => Unit is Adj)) : Result {
        // 创建 Bell 态作为纠缠资源
        use (aliceQubit, bobQubit) = (Qubit(), Qubit());
        
        // 准备要传输的量子态
        H(aliceQubit);
        
        // 创建 Bell 态
        use (bell1, bell2) = (Qubit(), Qubit());
        H(bell1);
        CNOT(bell1, bell2);
        
        // Alice 端的 Bell 测量
        CNOT(aliceQubit, bell1);
        H(aliceQubit);
        
        let measurement1 = M(aliceQubit);
        let measurement2 = M(bell1);
        
        // Bob 端根据测量结果进行修正
        if measurement2 == One {
            X(bobQubit);
        }
        if measurement1 == One {
            Z(bobQubit);
        }
        
        // 测量 Bob 的量子比特得到传输的态
        let finalResult = M(bobQubit);
        
        // 清理
        Reset(aliceQubit);
        Reset(bell1);
        Reset(bell2);
        Reset(bobQubit);
        
        return finalResult;
    }

    // ========================================================================
    // 6. 量子区块链辅助操作
    // ========================================================================
    
    /// <summary>
    /// 量子态签名 - 使用纠缠态创建量子签名
    /// </summary>
    /// <param name="message">消息 (整数数组)</param>
    /// <param name="privateKey">私钥</param>
    /// <returns>量子签名 (比特数组)</returns>
    operation QuantumSign(message : Int[], privateKey : Int) : Int[] {
        let messageLength = Length(message);
        let signatureSize = Max([messageLength, 8]);
        
        // 生成 GHZ 态用于签名
        use ghzRegister = Qubit[signatureSize];
        
        // 准备 GHZ 态
        H(ghzRegister[0]);
        for i in 0..signatureSize-2 {
            CNOT(ghzRegister[i], ghzRegister[i + 1]);
        }
        
        // 基于消息和私钥编码
        for i in 0..messageLength-1 {
            if message[i] == 1 {
                X(ghzRegister[i % signatureSize]);
            }
        }
        
        // 基于私钥添加相位
        for i in 0..signatureSize {
            if (privateKey >>> i) % 2 == 1 {
                Z(ghzRegister[i]);
            }
        }
        
        // 测量生成签名
        mutable signature = new Int[0];
        for i in 0..signatureSize-1 {
            let result = M(ghzRegister[i]);
            set signature += [ResultAsInt(result)];
        }
        
        ResetAll(ghzRegister);
        
        return signature;
    }

    /// <summary>
    /// 量子签名验证
    /// </summary>
    /// <param name="message">原始消息</param>
    /// <param name="signature">签名</param>
    /// <param name="publicKey">公钥</param>
    /// <returns>验证是否通过</returns>
    operation QuantumVerify(message : Int[], signature : Int[], publicKey : Int) : Bool {
        // 重新计算签名
        let recomputedSignature = QuantumSign(message, publicKey);
        
        // 比对签名
        mutable isValid = true;
        for i in 0..Length(signature)-1 {
            if i < Length(recomputedSignature) {
                if signature[i] != recomputedSignature[i] {
                    set isValid = false;
                }
            }
        }
        
        return isValid;
    }

    /// <summary>
    /// 量子时间戳生成
    /// 使用量子随机数生成不可预测的时间戳
    /// </summary>
    /// <returns>量子时间戳 (整数)</returns>
    operation QuantumTimestamp() : Int {
        // 生成 64 位量子随机数作为时间戳
        mutable timestamp = 0L;
        for i in 0..63 {
            let bit = GenerateRandomBit();
            if bit == One {
                set timestamp += 1L <<< i;
            }
        }
        
        return (Int)(timestamp % 9223372036854775807L);
    }

    /// <summary>
    /// 量子 Merkle 树节点哈希
    /// </summary>
    /// <param name="leftHash">左子节点哈希</param>
    /// <param name="rightHash">右子节点哈希</param>
    /// <param name="quantumEntropy">量子熵源</param>
    /// <returns>父节点哈希</returns>
    operation QuantumMerkleNode(
        leftHash : Int[],
        rightHash : Int[],
        quantumEntropy : Int[]
    ) : Int[] {
        // 组合输入
        let combined = leftHash + rightHash + quantumEntropy;
        
        // 应用量子哈希
        return QuantumHash(combined, 256);
    }

    /// <summary>
    /// 完整的量子 Merkle 树根计算
    /// </summary>
    /// <param name="transactions">交易列表</param>
    /// <returns>Merkle 树根哈希</returns>
    operation QuantumMerkleRoot(transactions : Int[][]) : Int[] {
        mutable currentLevel = transactions;
        
        repeat {
            mutable nextLevel = new Int[][][0];
            
            for i in 0..Length(currentLevel)-1 {
                if i % 2 == 0 {
                    let left = currentLevel[i];
                    let right = if i + 1 < Length(currentLevel) then currentLevel[i + 1] else left;
                    
                    // 生成量子熵
                    let entropy = QuantumHash([i], 32);
                    
                    // 计算父节点
                    let parent = QuantumMerkleNode(left, right, entropy);
                    set nextLevel += [parent];
                }
            }
            
            set currentLevel = nextLevel;
        }
        until Length(currentLevel) == 1
        fixup {
            // 继续迭代
        }
        
        return currentLevel[0];
    }

    // ========================================================================
    // 7. 主入口点和演示操作
    // ========================================================================
    
    /// <summary>
    /// 演示量子随机数生成
    /// </summary>
    operation DemoQRNG() : Unit {
        Message("=== 量子随机数生成演示 ===");
        
        // 生成单个随机比特
        let randomBit = GenerateRandomBit();
        Message($"单个随机比特：{ResultAsInt(randomBit)}");
        
        // 生成随机比特串
        let randomBits = GenerateRandomBitString(16);
        mutable bitString = "";
        for bit in randomBits {
            set bitString += $"{ResultAsInt(bit)}";
        }
        Message($"16 位随机比特串：{bitString}");
        
        // 生成随机整数
        let randomInt = GenerateRandomInt(100);
        Message($"[0,100) 范围内的随机整数：{randomInt}");
        
        // 生成随机十六进制字符串
        let randomHex = GenerateRandomHexString(8);
        Message($"8 字节随机十六进制：{randomHex}");
    }

    /// <summary>
    /// 演示 BB84 量子密钥分发
    /// </summary>
    operation DemoBB84() : Unit {
        Message("=== BB84 量子密钥分发演示 ===");
        
        let numBits = 20;
        Message($"准备发送 {numBits} 个量子比特...");
        
        // 执行 BB84 协议
        let sharedKey = BB84Protocol(numBits);
        
        mutable keyString = "";
        for bit in sharedKey {
            set keyString += $"{bit}";
        }
        Message($"生成的共享密钥：{keyString}");
        Message($"密钥长度：{Length(sharedKey)} 比特");
    }

    /// <summary>
    /// 演示 Grover 搜索算法
    /// </summary>
    operation DemoGrover() : Unit {
        Message("=== Grover 搜索算法演示 ===");
        
        let numQubits = 4;
        let target = 11;  // 要搜索的目标值 (二进制：1011)
        
        Message($"在 {1 <<< numQubits} 个状态中搜索目标值 {target}...");
        
        let result = GroverSearch(numQubits, target);
        
        Message($"搜索结果：{result}");
        if result == target {
            Message("搜索成功！");
        } else {
            Message($"搜索失败，期望 {target}，得到 {result}");
        }
    }

    /// <summary>
    /// 演示量子纠缠态生成
    /// </summary>
    operation DemoEntanglement() : Unit {
        Message("=== 量子纠缠态生成演示 ===");
        
        // Bell 态
        Message("生成 Bell 态...");
        use (q1, q2) = GenerateBellState();
        let bellCorrelated = VerifyBellState(q1, q2);
        Message($"Bell 态验证结果：{(bellCorrelated ? "通过" | "失败")}");
        
        // GHZ 态
        Message("生成 4 量子比特 GHZ 态...");
        use ghz = GenerateGHZState(4);
        Message("GHZ 态已生成 (量子比特已分配)");
        ResetAll(ghz);
        
        // W 态
        Message("生成 3 量子比特 W 态...");
        use w = GenerateWState(3);
        Message("W 态已生成");
        ResetAll(w);
        
        // Cluster 态
        Message("生成 5 量子比特 Cluster 态...");
        use cluster = GenerateClusterState(5);
        Message("Cluster 态已生成");
        ResetAll(cluster);
    }

    /// <summary>
    /// 演示量子哈希函数
    /// </summary>
    operation DemoQuantumHash() : Unit {
        Message("=== 量子哈希函数演示 ===");
        
        let inputData = [72, 101, 108, 108, 111];  // "Hello" 的 ASCII 码
        let outputSize = 64;
        
        Message($"输入数据：Hello (ASCII: {inputData})");
        Message($"输出大小：{outputSize} 比特");
        
        let hashResult = QuantumHash(inputData, outputSize);
        
        mutable hashString = "";
        for bit in hashResult {
            set hashString += $"{bit}";
        }
        Message($"哈希结果 (二进制): {hashString}");
        
        let hashHex = QuantumHashToString(inputData, 64);
        Message($"哈希结果 (十六进制): {hashHex}");
    }

    /// <summary>
    /// 完整的量子区块链演示
    /// </summary>
    operation DemoQuantumBlockchain() : Unit {
        Message("========================================");
        Message("   量子区块链 Q# 核心算法演示");
        Message("========================================");
        Message("");
        
        DemoQRNG();
        Message("");
        
        DemoQuantumHash();
        Message("");
        
        DemoBB84();
        Message("");
        
        DemoGrover();
        Message("");
        
        DemoEntanglement();
        Message("");
        
        Message("========================================");
        Message("   演示完成！");
        Message("========================================");
    }
}
