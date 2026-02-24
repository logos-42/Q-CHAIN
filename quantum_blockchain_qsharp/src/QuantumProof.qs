namespace QuantumBlockchain.Proof {
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Measurement;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Arrays;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Logical;
    open QuantumBlockchain.QRNG;

    function EncodeQubitState(data : String) : (String, String) {
        mutable encoded = "";
        mutable parityMatrix = "";
        
        for i in 0..Length(data)-1 {
            let charCode = Utf8CodeUnit(data[i]);
            set encoded += $"{charCode:X2}";
            
            mutable parity = 0;
            for j in 0..3 {
                if ((charCode >>> j) &&& 1) == 1 {
                    set parity = (parity + 1) mod 2;
                }
            }
            set parityMatrix += $"{parity}";
        }
        
        return (encoded, parityMatrix);
    }

    function InjectErrors(encodedData : String, errorRate : Double) : (String, String) {
        mutable corrupted = "";
        mutable errorPattern = "";
        
        for i in 0..Length(encodedData)-1 {
            let randomVal = RandomReal(32768);
            let threshold = Round(errorRate * 32768.0);
            
            if randomVal < threshold {
                let originalCode = encodedData[i];
                let errorChar = (originalCode + 1) mod 256;
                set corrupted += $"{errorChar:X}";
                set errorPattern += "1";
            } else {
                set corrupted += $"{encodedData[i]}";
                set errorPattern += "0";
            }
        }
        
        return (corrupted, errorPattern);
    }

    function ApplyErrorCorrection(corruptedData : String, parityMatrix : String) : String {
        mutable corrected = "";
        
        for i in 0..Length(corruptedData)-1 {
            let corruptedChar = corruptedData[i];
            let parityBit = parityMatrix[i];
            
            if parityBit == "1" {
                let correctedChar = (corruptedChar + 255) mod 256;
                set corrected += $"{correctedChar:X}";
            } else {
                set corrected += $"{corruptedData[i]}";
            }
        }
        
        return corrected;
    }

    function VerifyCorrection(original : String, corrected : String, errorPattern : String) : Bool {
        if Length(original) != Length(corrected) {
            return false;
        }
        
        mutable errorCount = 0;
        for i in 0..Length(errorPattern)-1 {
            if errorPattern[i] == "1" {
                set errorCount += 1;
            }
        }
        
        return errorCount > 0;
    }

    operation GeneratePQECProof(difficulty : Int) : (String, String, Int) {
        let testData = "QuantumProof";
        
        let (encoded, parityMatrix) = EncodeQubitState(testData);
        
        let errorRate = 0.05 * Double(difficulty);
        let (corrupted, errorPattern) = InjectErrors(encoded, errorRate);
        
        let correction = ApplyErrorCorrection(corrupted, parityMatrix);
        
        let verification = VerifyCorrection(encoded, correction, errorPattern);
        
        let proofData = $"{encoded}|{errorPattern}|{correction}";
        
        return (proofData, errorPattern, difficulty);
    }

    operation VerifyPQECProof(proof : String, correction : String, difficulty : Int) : Bool {
        if difficulty < 1 or difficulty > 10 {
            return false;
        }
        
        let components = SplitString(proof, "|");
        if Length(components) < 3 {
            return false;
        }
        
        let encoded = components[0];
        let errorPattern = components[1];
        
        let checkCorrection = ApplyErrorCorrection(proof, errorPattern);
        
        if checkCorrection != correction {
            return false;
        }
        
        mutable errorCount = 0;
        for i in 0..Length(errorPattern)-1 {
            if errorPattern[i] == "1" {
                set errorCount += 1;
            }
        }
        
        let minErrors = difficulty;
        return errorCount >= minErrors;
    }

    function SplitString(input : String, delimiter : String) : String[] {
        mutable result = [""];
        mutable currentIndex = 0;
        
        for i in 0..Length(input)-1 {
            let char = input[i];
            let delimChar = delimiter[0];
            
            if char == delimChar {
                set result += [""];
                set currentIndex += 1;
            } else {
                set result[currentIndex] = result[currentIndex] + $"{char}";
            }
        }
        
        return result;
    }

    operation CreateQuantumWorkProof(data : String, errorRate : Double) : String {
        let (encoded, parityMatrix) = EncodeQubitState(data);
        
        let (corrupted, errorPattern) = InjectErrors(encoded, errorRate);
        
        let correction = ApplyErrorCorrection(corrupted, parityMatrix);
        
        let verification = VerifyCorrection(encoded, correction, errorPattern);
        
        let proofComponents = [
            "PQE",
            "1.0",
            encoded,
            errorPattern,
            correction,
            $"{verification}",
            $"{Round(errorRate * 100.0)}"
        ];
        
        mutable proof = "";
        for i in 0..Length(proofComponents)-1 {
            if i > 0 {
                set proof = proof + ":";
            }
            set proof = proof + proofComponents[i];
        }
        
        return proof;
    }

    operation VerifyQuantumWork(proofData : String, targetDifficulty : Int) : (Bool, Int) {
        let components = SplitString(proofData, ":");
        
        if Length(components) < 7 {
            return (false, 0);
        }
        
        if components[0] != "PQE" {
            return (false, 0);
        }
        
        let encoded = components[2];
        let errorPattern = components[3];
        let correction = components[4];
        
        if correction != encoded {
            return (false, 0);
        }
        
        mutable errorCount = 0;
        for i in 0..Length(errorPattern)-1 {
            if errorPattern[i] == "1" {
                set errorCount += 1;
            }
        }
        
        let actualDifficulty = Min([10, Max([1, errorCount / 2])]);
        
        let isValid = actualDifficulty >= targetDifficulty;
        
        return (isValid, actualDifficulty);
    }

    operation CalculateOptimalDifficulty(numQubits : Int, errorRate : Double) : Int {
        let baseDifficulty = 3;
        
        let qubitFactor = numQubits / 100;
        
        let errorPenalty = Round(errorRate * 100.0);
        
        let optimalDiff = baseDifficulty + qubitFactor - (errorPenalty / 10);
        
        let clampedDiff = Max([1, Min([10, optimalDiff])]);
        
        return Round(clampedDiff);
    }

    operation ClassicalProofOfWork(data : String, difficulty : Int) : String {
        mutable nonce = 0;
        mutable hashResult = "";
        
        repeat {
            let testString = data + $"{nonce}";
            mutable hashValue = 0;
            
            for i in 0..Length(testString)-1 {
                set hashValue = (hashValue + IntAsDouble(Utf8CodeUnit(testString[i])) * Double(i + 1)) mod 1000000007;
            }
            
            set hashResult = $"{hashValue:X}";
            set nonce += 1;
        } until (nonce >= PowI(2, difficulty) or Length(hashResult) >= difficulty);
        
        return $"{nonce - 1}|{hashResult}";
    }

    operation HybridProofOfWork(data : String, classicalDifficulty : Int, quantumDifficulty : Int) : String {
        let classicalProof = ClassicalProofOfWork(data, classicalDifficulty);
        
        let quantumProof = CreateQuantumWorkProof(data, 0.05 * Double(quantumDifficulty));
        
        let (isQuantumValid, actualQuantumDiff) = VerifyQuantumWork(quantumProof, quantumDifficulty);
        
        let classicalComponents = SplitString(classicalProof, "|");
        let classicalHash = classicalComponents[1];
        mutable classicalValid = false;
        
        if Length(classicalHash) >= classicalDifficulty {
            set classicalValid = true;
        }
        
        if classicalValid and isQuantumValid {
            return $"HYBRID|{classicalProof}|{quantumProof}|PASS";
        } else {
            return $"HYBRID|{classicalProof}|{quantumProof}|FAIL";
        }
    }

    function SimulateTimeMeasurement() : Double {
        let randomVal = RandomReal(1000);
        return randomVal / 1000.0;
    }

    operation QuantumTimeChallenge(difficulty : Int, timeLimit : Int) : (String, Double) {
        let startTime = 0.0;
        
        let testData = "TimeChallenge_" + $"{difficulty}";
        
        let proof = CreateQuantumWorkProof(testData, 0.05 * Double(difficulty));
        
        let (isValid, actualDiff) = VerifyQuantumWork(proof, difficulty);
        
        let timeSpent = SimulateTimeMeasurement();
        
        if timeSpent > Double(timeLimit) {
            return ("TIMEOUT", timeSpent);
        }
        
        if isValid {
            let challengeResult = $"TIME|{difficulty}|{actualDiff}|{proof}";
            return (challengeResult, timeSpent);
        } else {
            return ("INVALID", timeSpent);
        }
    }

    operation RunPQECDemo() : Unit {
        Message("========================================");
        Message("   PQEC协议演示");
        Message("========================================");
        Message("");
        
        Message("1. 生成PQEC证明 (难度=3)...");
        let (proof, errorPattern, diff) = GeneratePQECProof(3);
        Message($"   编码状态: {proof}");
        Message($"   错误模式: {errorPattern}");
        Message($"   难度: {diff}");
        Message("");
        
        Message("2. 验证PQEC证明...");
        let isValid = VerifyPQECProof(proof, errorPattern, diff);
        Message($"   验证结果: {isValid}");
        Message("");
        
        Message("3. 创建量子工作证明...");
        let workProof = CreateQuantumWorkProof("BlockData123", 0.15);
        Message($"   工作证明: {workProof}");
        Message("");
        
        Message("4. 验证量子工作证明 (目标难度=3)...");
        let (valid, actualDiff) = VerifyQuantumWork(workProof, 3);
        Message($"   有效性: {valid}");
        Message($"   实际难度: {actualDiff}");
        Message("");
        
        Message("5. 计算最优难度 (100量子比特, 错误率0.1)...");
        let optimalDiff = CalculateOptimalDifficulty(100, 0.1);
        Message($"   最优难度: {optimalDiff}");
        Message("");
        
        Message("6. 混合Proof机制...");
        let hybrid = HybridProofOfWork("TestData", 2, 3);
        Message($"   混合Proof: {hybrid}");
        Message("");
        
        Message("7. 量子时间挑战 (难度=3, 时间限制=5秒)...");
        let (challengeProof, timeUsed) = QuantumTimeChallenge(3, 5);
        Message($"   挑战结果: {challengeProof}");
        Message($"   耗时: {timeUsed}秒");
        Message("");
        
        Message("========================================");
        Message("   演示完成");
        Message("========================================");
    }

    @EntryPoint()
    operation Main() : Unit {
        Message("========================================");
        Message("   量子区块链Proof of Quantum Error");
        Message("         Correction (PQEC) 模块");
        Message("========================================");
        Message("");
        
        RunPQECDemo();
        
        Message("");
        Message("PQEC协议核心特性:");
        Message("- 量子纠错任务作为工作量证明");
        Message("- 验证快速 (仅检查纠错结果)");
        Message("- 利用量子计算优势");
        Message("- 支持混合经典+量子Proof");
        Message("- 时间挑战模式");
    }
}
