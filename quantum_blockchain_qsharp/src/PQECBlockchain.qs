namespace QuantumBlockchain.PQEC {
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Measurement;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Arrays;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Logical;
    open QuantumBlockchain.Proof;
    open QuantumBlockchain.QEC;
    open QuantumBlockchain.QRNG;

    newtype PQECBlock = (
        index: Int,
        timestamp: String,
        data: String,
        previousHash: String,
        quantumProof: String,
        quantumSignature: String,
        hash: String
    );

    function GetPQECIndex(block : PQECBlock) : Int {
        let (idx, _, _, _, _, _, _) = block!;
        return idx;
    }

    function GetPQECTimestamp(block : PQECBlock) : String {
        let (_, ts, _, _, _, _, _) = block!;
        return ts;
    }

    function GetPQECData(block : PQECBlock) : String {
        let (_, _, data, _, _, _, _) = block!;
        return data;
    }

    function GetPQECPreviousHash(block : PQECBlock) : String {
        let (_, _, _, prevHash, _, _, _) = block!;
        return prevHash;
    }

    function GetPQECQuantumProof(block : PQECBlock) : String {
        let (_, _, _, _, qProof, _, _) = block!;
        return qProof;
    }

    function GetPQECQuantumSignature(block : PQECBlock) : String {
        let (_, _, _, _, _, qSig, _) = block!;
        return qSig;
    }

    function GetPQECHash(block : PQECBlock) : String {
        let (_, _, _, _, _, _, hash) = block!;
        return hash;
    }

    function CreatePQECBlockTuple(
        idx: Int,
        ts: String,
        data: String,
        prevHash: String,
        qProof: String,
        qSig: String,
        hash: String
    ) : PQECBlock {
        return (idx, ts, data, prevHash, qProof, qSig, hash)!;
    }

    operation CalculatePQECBlockHash(
        blockData: String,
        previousHash: String,
        quantumProof: String,
        quantumSignature: String
    ) : String {
        mutable hashValue = 0;
        
        for i in 0..Length(blockData)-1 {
            set hashValue = (hashValue + IntAsDouble(Utf8CodeUnit(blockData[i])) * Double(i + 1)) mod 1000000007;
        }
        for i in 0..Length(previousHash)-1 {
            set hashValue = (hashValue + IntAsDouble(Utf8CodeUnit(previousHash[i])) * Double(i + 1)) mod 1000000007;
        }
        for i in 0..Length(quantumProof)-1 {
            set hashValue = (hashValue + IntAsDouble(Utf8CodeUnit(quantumProof[i])) * Double(i + 1)) mod 1000000007;
        }
        for i in 0..Length(quantumSignature)-1 {
            set hashValue = (hashValue + IntAsDouble(Utf8CodeUnit(quantumSignature[i])) * Double(i + 1)) mod 1000000007;
        }
        
        mutable hashHex = $"{hashValue:X}";
        
        let quantumBits = GenerateRandomBits(64);
        let hexPart = BitStringToHex(quantumBits);
        set hashHex = hashHex + hexPart;
        
        return hashHex;
    }

    operation GeneratePQECTimestamp() : String {
        let randomBits = GenerateRandomBits(32);
        return BitStringToHex(randomBits);
    }

    operation ApplyQuantumErrorCorrectionProof(difficulty : Int) : (String, String, Bool) {
        let testData = "PQEC_Block_Proof_" + $"{difficulty}";
        
        let (encoded, parityMatrix) = EncodeQubitState(testData);
        
        let errorRate = 0.05 * Double(difficulty);
        let (corrupted, errorPattern) = InjectErrors(encoded, errorRate);
        
        let correction = ApplyErrorCorrection(corrupted, parityMatrix);
        
        let verification = VerifyCorrection(encoded, correction, errorPattern);
        
        let proofComponents = [
            "PQEC",
            "1.0",
            encoded,
            errorPattern,
            correction,
            $"{verification}",
            $"{Round(errorRate * 100.0)}",
            $"{difficulty}"
        ];
        
        mutable proof = "";
        for i in 0..Length(proofComponents)-1 {
            if i > 0 {
                set proof = proof + ":";
            }
            set proof = proof + proofComponents[i];
        }
        
        return (proof, errorPattern, verification);
    }

    operation VerifyPQECBlockProof(proof : String, difficulty : Int) : Bool {
        let components = SplitString(proof, ":");
        
        if Length(components) < 8 {
            return false;
        }
        
        if components[0] != "PQEC" {
            return false;
        }
        
        let encoded = components[2];
        let errorPattern = components[3];
        let correction = components[4];
        
        let checkCorrection = ApplyErrorCorrection(encoded, errorPattern);
        
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

    operation CreateGenesisBlockWithPQEC() : PQECBlock {
        Message("========================================");
        Message("  使用PQEC创建创世区块");
        Message("========================================");
        
        let genesisData = "Genesis Block - Quantum PQEC Blockchain v1.0";
        let previousHash = "0000000000000000000000000000000000000000000000000000000000000000";
        let timestamp = "0";
        let index = 0;
        
        let difficulty = 2;
        
        let (qProof, errorPattern, verification) = ApplyQuantumErrorCorrectionProof(difficulty);
        Message($"  PQEC证明生成: 难度={difficulty}, 错误数={errorPattern}");
        
        let qSignature = GenerateQuantumSignature();
        
        let blockHash = CalculatePQECBlockHash(genesisData, previousHash, qProof, qSignature);
        
        let genesisBlock = CreatePQECBlockTuple(
            index,
            timestamp,
            genesisData,
            previousHash,
            qProof,
            qSignature,
            blockHash
        );
        
        Message($"  创世区块索引: {index}");
        Message($"  创世区块哈希: {blockHash}");
        Message("");
        
        return genesisBlock;
    }

    operation MineBlockWithPQEC(previousBlock : PQECBlock, data : String, difficulty : Int) : PQECBlock {
        let newIndex = GetPQECIndex(previousBlock) + 1;
        let newTimestamp = GeneratePQECTimestamp();
        let newPreviousHash = GetPQECHash(previousBlock);
        
        Message($"  挖矿区块 #{newIndex} (难度={difficulty})...");
        
        let (qProof, errorPattern, verification) = ApplyQuantumErrorCorrectionProof(difficulty);
        Message($"    PQEC证明: {errorPattern}");
        
        let qSignature = GenerateQuantumSignature();
        
        let blockHash = CalculatePQECBlockHash(data, newPreviousHash, qProof, qSignature);
        
        let newBlock = CreatePQECBlockTuple(
            newIndex,
            newTimestamp,
            data,
            newPreviousHash,
            qProof,
            qSignature,
            blockHash
        );
        
        Message($"    区块 #{newIndex} 挖矿成功!");
        Message($"    哈希: {blockHash}");
        
        return newBlock;
    }

    operation VerifyBlockWithPQEC(block : PQECBlock, difficulty : Int) : Bool {
        let blockIndex = GetPQECIndex(block);
        let blockData = GetPQECData(block);
        let blockPrevHash = GetPQECPreviousHash(block);
        let blockQProof = GetPQECQuantumProof(block);
        let blockQSig = GetPQECQuantumSignature(block);
        let blockHash = GetPQECHash(block);
        
        let calculatedHash = CalculatePQECBlockHash(blockData, blockPrevHash, blockQProof, blockQSig);
        
        if calculatedHash != blockHash {
            Message($"  区块 #{blockIndex}: 哈希验证失败");
            return false;
        }
        
        let proofValid = VerifyPQECBlockProof(blockQProof, difficulty);
        
        if not proofValid {
            Message($"  区块 #{blockIndex}: PQEC证明验证失败");
            return false;
        }
        
        Message($"  区块 #{blockIndex}: 验证通过");
        
        return true;
    }

    operation AddBlockWithProof(chain : PQECBlock[], data : String, difficulty : Int) : PQECBlock[] {
        let chainLength = Length(chain);
        
        if chainLength == 0 {
            Message("错误: 链为空，请先创建创世区块");
            return chain;
        }
        
        let lastBlock = chain[chainLength - 1];
        let newBlock = MineBlockWithPQEC(lastBlock, data, difficulty);
        
        mutable newChain = chain;
        set newChain += [newBlock];
        
        return newChain;
    }

    operation IsChainValidWithPQEC(chain : PQECBlock[], difficulty : Int) : Bool {
        let chainLength = Length(chain);
        
        if chainLength == 0 {
            Message("链为空，无效");
            return false;
        }
        
        let firstBlock = chain[0];
        let firstPrevHash = GetPQECPreviousHash(firstBlock);
        if firstPrevHash != "0000000000000000000000000000000000000000000000000000000000000000" {
            Message("创世区块previousHash不正确");
            return false;
        }
        
        let firstProof = GetPQECQuantumProof(firstBlock);
        if not VerifyPQECBlockProof(firstProof, difficulty) {
            Message("创世区块PQEC证明无效");
            return false;
        }
        
        for i in 1..chainLength-1 {
            let currentBlock = chain[i];
            let previousBlock = chain[i-1];
            
            let storedPrevHash = GetPQECPreviousHash(currentBlock);
            let previousBlockHash = GetPQECHash(previousBlock);
            
            if storedPrevHash != previousBlockHash {
                Message($"区块 {i}: previousHash链接错误");
                return false;
            }
            
            if not VerifyBlockWithPQEC(currentBlock, difficulty) {
                Message($"区块 {i}: 验证失败");
                return false;
            }
        }
        
        Message("========================================");
        Message("  区块链PQEC验证通过 - 链有效!");
        Message("========================================");
        
        return true;
    }

    function AdjustDifficulty(previousDifficulty : Int, blockTime : Double, targetTime : Double) : Int {
        let ratio = blockTime / targetTime;
        
        mutable newDifficulty = previousDifficulty;
        
        if ratio < 0.5 {
            set newDifficulty = previousDifficulty + 2;
        }
        elif ratio < 0.8 {
            set newDifficulty = previousDifficulty + 1;
        }
        elif ratio > 2.0 {
            set newDifficulty = previousDifficulty - 2;
        }
        elif ratio > 1.5 {
            set newDifficulty = previousDifficulty - 1;
        }
        
        let minDiff = 1;
        let maxDiff = 10;
        
        if newDifficulty < minDiff {
            set newDifficulty = minDiff;
        }
        if newDifficulty > maxDiff {
            set newDifficulty = maxDiff;
        }
        
        return newDifficulty;
    }

    operation PrintPQECBlock(block : PQECBlock) : Unit {
        let idx = GetPQECIndex(block);
        let ts = GetPQECTimestamp(block);
        let data = GetPQECData(block);
        let prevHash = GetPQECPreviousHash(block);
        let qProof = GetPQECQuantumProof(block);
        let qSig = GetPQECQuantumSignature(block);
        let hash = GetPQECHash(block);
        
        Message("----------------------------------------");
        Message($"区块 #{idx}");
        Message($"  时间戳: {ts}");
        Message($"  数据: {data}");
        Message($"  前驱哈希: {prevHash}");
        Message($"  PQEC证明: {qProof}");
        Message($"  量子签名: {qSig}");
        Message($"  区块哈希: {hash}");
        Message("----------------------------------------");
    }

    operation GetPQECChainInfo(chain : PQECBlock[]) : Unit {
        let length = Length(chain);
        Message("");
        Message("========================================");
        Message("  区块链信息");
        Message("========================================");
        Message($"  区块链长度: {length} 个区块");
        
        if length > 0 {
            let firstBlock = chain[0];
            let lastBlock = chain[length-1];
            Message($"  创世区块: 索引={GetPQECIndex(firstBlock)}");
            Message($"  最新区块: 索引={GetPQECIndex(lastBlock)}");
            Message($"  最新哈希: {GetPQECHash(lastBlock)}");
        }
        Message("========================================");
        Message("");
    }

    operation RunPQECBlockchainDemo() : Unit {
        Message("");
        Message("########################################");
        Message("#                                      #");
        Message("#   量子区块链 PQEC 共识模块演示        #");
        Message("#   Post-Quantum Error Correction     #");
        Message("#                                      #");
        Message("########################################");
        Message("");
        
        let initialDifficulty = 2;
        
        Message("========================================");
        Message("  步骤1: 创建创世区块 (PQEC)");
        Message("========================================");
        let genesisBlock = CreateGenesisBlockWithPQEC();
        PrintPQECBlock(genesisBlock);
        
        mutable chain = [genesisBlock];
        
        Message("");
        Message("========================================");
        Message("  步骤2: 添加第一个区块");
        Message("========================================");
        set chain = AddBlockWithProof(chain, "Alice -> Bob: 10 QTC", initialDifficulty);
        
        Message("");
        Message("========================================");
        Message("  步骤3: 添加第二个区块");
        Message("========================================");
        set chain = AddBlockWithProof(chain, "Bob -> Charlie: 5 QTC", initialDifficulty);
        
        Message("");
        Message("========================================");
        Message("  步骤4: 添加第三个区块");
        Message("========================================");
        set chain = AddBlockWithProof(chain, "Charlie -> Dave: 3 QTC", initialDifficulty);
        
        Message("");
        Message("========================================");
        Message("  步骤5: 添加第四个区块");
        Message("========================================");
        set chain = AddBlockWithProof(chain, "Dave -> Eve: 7 QTC", initialDifficulty);
        
        Message("");
        Message("========================================");
        Message("  步骤6: 添加第五个区块");
        Message("========================================");
        set chain = AddBlockWithProof(chain, "Eve -> Frank: 2 QTC", initialDifficulty);
        
        GetPQECChainInfo(chain);
        
        Message("========================================");
        Message("  步骤7: 验证区块链");
        Message("========================================");
        let isValid = IsChainValidWithPQEC(chain, initialDifficulty);
        Message($"  验证结果: {isValid}");
        
        Message("");
        Message("========================================");
        Message("  步骤8: 打印所有区块");
        Message("========================================");
        for i in 0..Length(chain)-1 {
            PrintPQECBlock(chain[i]);
            Message("");
        }
        
        Message("");
        Message("========================================");
        Message("  步骤9: 难度调整演示");
        Message("========================================");
        
        let testCases = [
            (5.0, 10.0),
            (15.0, 10.0),
            (8.0, 10.0),
            (20.0, 10.0),
            (2.0, 10.0)
        ];
        
        Message("  当前难度: 2");
        mutable currentDiff = 2;
        
        for idx in 0..Length(testCases)-1 {
            let (blockTime, targetTime) = testCases[idx];
            set currentDiff = AdjustDifficulty(currentDiff, blockTime, targetTime);
            Message($"    出块时间: {blockTime}s -> 调整后难度: {currentDiff}");
        }
        
        Message("");
        Message("========================================");
        Message("  PQEC共识模块演示完成!");
        Message("========================================");
        Message("");
        Message("核心特性:");
        Message("  - 量子纠错任务作为工作量证明");
        Message("  - 基于Shor/Steane码的PQEC证明");
        Message("  - 区块链接验证");
        Message("  - 动态难度调整");
        Message("  - 混合量子-经典共识");
        Message("");
        Message("########################################");
    }

    @EntryPoint()
    operation Main() : Unit {
        RunPQECBlockchainDemo();
    }
}
