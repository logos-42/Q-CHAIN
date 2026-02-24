namespace QuantumBlockchain.QHash {
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Measurement;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Arrays;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Canon;

    function StringToBytes(data : String) : Int[] {
        mutable bytes = new Int[0];
        for i in 0..Length(data)-1 {
            let charCode = (int)(data[i]) - 32;
            set bytes += [charCode % 128];
        }
        return bytes;
    }

    function SimpleHash(data : String) : String {
        mutable hash = 0;
        for i in 0..Length(data)-1 {
            let charCode = (int)(data[i]);
            set hash = (hash * 31 + charCode) % 2147483647;
        }
        return $"{hash:X8}";
    }

    operation ApplyQuantumCircuit(qubits : Qubit[], asciiCodes : Int[]) : Unit {
        let numQubits = Length(qubits);
        
        for i in 0..numQubits-1 {
            let asciiCode = if i < Length(asciiCodes) then asciiCodes[i] else 0;
            
            if asciiCode % 2 == 1 {
                X(qubits[i]);
            }
            
            let rotationAngle = PI() * IntAsDouble(asciiCode % 16) / 8.0;
            Rz(rotationAngle, qubits[i]);
        }
        
        ApplyToEach(H, qubits);
        
        for i in 0..numQubits-2 {
            CNOT(qubits[i], qubits[i + 1]);
        }
        
        for i in 0..numQubits-1 {
            H(qubits[i]);
            let phase = PI() * IntAsDouble(i + 1) / 4.0;
            Rz(phase, qubits[i]);
        }
        
        for i in 0..numQubits-2 {
            if i % 2 == 0 {
                CNOT(qubits[i], qubits[i + 1]);
            }
        }
    }

    operation QuantumHashCircuit(data : String) : String {
        let numQubits = 8;
        let asciiCodes = StringToBytes(data);
        
        use qubits = Qubit[numQubits];
        
        ApplyQuantumCircuit(qubits, asciiCodes);
        
        mutable measurements = new Result[0];
        for i in 0..numQubits-1 {
            let result = M(qubits[i]);
            set measurements += [result];
        }
        
        ResetAll(qubits);
        
        mutable bitString = "";
        for bit in measurements {
            set bitString += $"{ResultAsInt(bit)}";
        }
        
        return bitString;
    }

    function BitsToHex(bitArray : Result[]) : String {
        let numNibbles = (Length(bitArray) + 3) / 4;
        mutable hexString = "";
        
        for i in 0..numNibbles-1 {
            mutable nibble = 0;
            for j in 0..3 {
                let bitIndex = i * 4 + j;
                if bitIndex < Length(bitArray) and bitArray[bitIndex] == One {
                    set nibble += 1 <<< (3 - j);
                }
            }
            set hexString += $"{nibble:X}";
        }
        
        return hexString;
    }

    operation QuantumHashCircuitHex(data : String) : String {
        let numQubits = 8;
        let asciiCodes = StringToBytes(data);
        
        use qubits = Qubit[numQubits];
        
        ApplyQuantumCircuit(qubits, asciiCodes);
        
        mutable measurements = new Result[0];
        for i in 0..numQubits-1 {
            let result = M(qubits[i]);
            set measurements += [result];
        }
        
        ResetAll(qubits);
        
        return BitsToHex(measurements);
    }

    operation RunMultipleHashTrials(data : String, numTrials : Int) : String[] {
        mutable results = new String[0];
        
        for _ in 0..numTrials-1 {
            let hashResult = QuantumHashCircuitHex(data);
            set results += [hashResult];
        }
        
        return results;
    }

    function XorStrings(s1 : String, s2 : String) : String {
        mutable result = "";
        let len1 = Length(s1);
        let len2 = Length(s2);
        let minLen = Min([len1, len2]);
        
        for i in 0..minLen-1 {
            let v1 = (int)(s1[i]);
            let v2 = (int)(s2[i]);
            let xorVal = v1 ^^^ v2;
            set result += "0123456789ABCDEF"[(xorVal / 16) % 16];
            set result += "0123456789ABCDEF"[xorVal % 16];
        }
        
        return result;
    }

    operation HybridHash(data : String, outputSize : Int) : String {
        let classicalHash = SimpleHash(data);
        
        let quantumEntropy = QuantumHashCircuitHex(data);
        
        let combined = XorStrings(classicalHash, quantumEntropy);
        
        let finalHash = combined[...Min([Length(combined)-1, (outputSize / 4) - 1])];
        
        return finalHash;
    }

    operation HybridHashDetailed(data : String, outputSize : Int) : (String, String, String) {
        let classicalHash = SimpleHash(data);
        
        let quantumEntropy = QuantumHashCircuitHex(data);
        
        let combined = XorStrings(classicalHash, quantumEntropy);
        
        let finalHash = combined[...Min([Length(combined)-1, (outputSize / 4) - 1])];
        
        return (classicalHash, quantumEntropy, finalHash);
    }

    @EntryPoint()
    operation Main() : Unit {
        Message("========================================");
        Message("   量子哈希函数模块测试");
        Message("========================================");
        Message("");
        
        let testData = "QuantumBlockchain";
        Message($"测试数据: {testData}");
        Message("");
        
        Message("--- 量子哈希电路 (QuantumHashCircuit) ---");
        let quantumHash = QuantumHashCircuit(testData);
        Message($"量子哈希 (二进制): {quantumHash}");
        
        let quantumHashHex = QuantumHashCircuitHex(testData);
        Message($"量子哈希 (十六进制): {quantumHashHex}");
        Message("");
        
        Message("--- 多次运行测试 ---");
        let trials = RunMultipleHashTrials(testData, 5);
        for i in 0..Length(trials)-1 {
            Message($"试验 {i+1}: {trials[i]}");
        }
        Message("");
        
        Message("--- 混合哈希函数 (HybridHash) ---");
        let outputSize = 64;
        let hybridResult = HybridHash(testData, outputSize);
        Message($"混合哈希 ({outputSize}位): {hybridResult}");
        Message("");
        
        Message("--- 混合哈希详细输出 ---");
        let (classicalHash, quantumEntropy, finalHash) = HybridHashDetailed(testData, outputSize);
        Message($"经典哈希: {classicalHash}");
        Message($"量子熵源: {quantumEntropy}");
        Message($"最终哈希: {finalHash}");
        Message("");
        
        Message("========================================");
        Message("   测试完成！");
        Message("========================================");
    }
}
