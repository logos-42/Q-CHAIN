namespace QuantumBlockchain.Blockchain {
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Measurement;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Arrays;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Logical;
    open QuantumBlockchain.QRNG;

    newtype Block = (
        index: Int,
        timestamp: String,
        data: String,
        previousHash: String,
        quantumSignature: String,
        hash: String
    );

    function GetIndex(block : Block) : Int {
        let (idx, _, _, _, _, _) = block!;
        return idx;
    }

    function GetTimestamp(block : Block) : String {
        let (_, ts, _, _, _, _) = block!;
        return ts;
    }

    function GetData(block : Block) : String {
        let (_, _, data, _, _, _) = block!;
        return data;
    }

    function GetPreviousHash(block : Block) : String {
        let (_, _, _, prevHash, _, _) = block!;
        return prevHash;
    }

    function GetQuantumSignature(block : Block) : String {
        let (_, _, _, _, sig, _) = block!;
        return sig;
    }

    function GetHash(block : Block) : String {
        let (_, _, _, _, _, hash) = block!;
        return hash;
    }

    function CreateBlockTuple(
        idx: Int,
        ts: String,
        data: String,
        prevHash: String,
        sig: String,
        hash: String
    ) : Block {
        return (idx, ts, data, prevHash, sig, hash)!;
    }

    operation SimpleHash(data : String, previousHash : String, signature : String) : String {
        mutable hashValue = "";
        mutable seed = 0;
        
        for i in 0..Length(data)-1 {
            set seed = (seed + IntAsDouble(Utf8CodeUnit(data[i])) * Double(i + 1)) mod 1000000007;
        }
        for i in 0..Length(previousHash)-1 {
            set seed = (seed + IntAsDouble(Utf8CodeUnit(previousHash[i])) * Double(i + 1)) mod 1000000007;
        }
        for i in 0..Length(signature)-1 {
            set seed = (seed + IntAsDouble(Utf8CodeUnit(signature[i])) * Double(i + 1)) mod 1000000007;
        }
        
        set hashValue = $"{seed:X}";
        
        let quantumBits = GenerateRandomBits(128);
        let hexPart = BitStringToHex(quantumBits);
        set hashValue = hashValue + hexPart;
        
        return hashValue;
    }

    operation GenerateBlockTimestamp() : String {
        let randomBits = GenerateRandomBits(32);
        let hexTime = BitStringToHex(randomBits);
        return hexTime;
    }

    operation CalculateBlockHash(block : Block) : String {
        let data = GetData(block);
        let previousHash = GetPreviousHash(block);
        let signature = GetQuantumSignature(block);
        
        let hashValue = SimpleHash(data, previousHash, signature);
        
        return hashValue;
    }

    operation CreateGenesisBlock() : Block {
        Message("创建创世区块...");
        
        let genesisData = "Genesis Block - Quantum Blockchain v1.0";
        let previousHash = "0000000000000000000000000000000000000000000000000000000000000000";
        let timestamp = "0";
        let index = 0;
        
        let signature = GenerateQuantumSignature();
        let blockHash = SimpleHash(genesisData, previousHash, signature);
        
        let genesisBlock = CreateBlockTuple(index, timestamp, genesisData, previousHash, signature, blockHash);
        
        Message($"创世区块索引: {index}");
        Message($"创世区块哈希: {blockHash}");
        
        return genesisBlock;
    }

    operation AddBlock(existingChain : Block[], data : String) : Block[] {
        let chainLength = Length(existingChain);
        
        if chainLength == 0 {
            Message("错误: 链为空，请先创建创世区块");
            return existingChain;
        }
        
        let lastBlock = existingChain[chainLength - 1];
        let newIndex = GetIndex(lastBlock) + 1;
        let newTimestamp = GenerateBlockTimestamp();
        let newPreviousHash = GetHash(lastBlock);
        
        let signature = GenerateQuantumSignature();
        let blockHash = SimpleHash(data, newPreviousHash, signature);
        
        let newBlock = CreateBlockTuple(newIndex, newTimestamp, data, newPreviousHash, signature, blockHash);
        
        Message($"添加新区块: 索引={newIndex}, 哈希={blockHash}");
        
        mutable newChain = existingChain;
        set newChain += [newBlock];
        
        return newChain;
    }

    operation IsChainValid(chain : Block[]) : Bool {
        let chainLength = Length(chain);
        
        if chainLength == 0 {
            Message("链为空，无效");
            return false;
        }
        
        if chainLength == 1 {
            let block = chain[0];
            let prevHash = GetPreviousHash(block);
            if prevHash != "0000000000000000000000000000000000000000000000000000000000000000" {
                Message("创世区块previousHash不正确");
                return false;
            }
            Message("单区块链有效（创世区块）");
            return true;
        }
        
        for i in 1..chainLength-1 {
            let currentBlock = chain[i];
            let previousBlock = chain[i-1];
            
            let storedHash = GetHash(currentBlock);
            let calculatedHash = CalculateBlockHash(currentBlock);
            
            if storedHash != calculatedHash {
                Message($"区块 {i} 哈希不匹配: {storedHash} != {calculatedHash}");
                return false;
            }
            
            let storedPrevHash = GetPreviousHash(currentBlock);
            let previousBlockHash = GetHash(previousBlock);
            
            if storedPrevHash != previousBlockHash {
                Message($"区块 {i} previousHash不匹配");
                return false;
            }
            
            Message($"区块 {i} 验证通过");
        }
        
        Message("区块链完整性验证通过");
        return true;
    }

    function GetChainInfo(chain : Block[]) : Unit {
        let length = Length(chain);
        Message($"区块链长度: {length}");
        
        if length > 0 {
            let firstBlock = chain[0];
            let lastBlock = chain[length-1];
            Message($"创世区块索引: {GetIndex(firstBlock)}, 哈希: {GetHash(firstBlock)}");
            Message($"最新区块索引: {GetIndex(lastBlock)}, 哈希: {GetHash(lastBlock)}");
        }
    }

    operation PrintBlock(block : Block) : Unit {
        let idx = GetIndex(block);
        let ts = GetTimestamp(block);
        let data = GetData(block);
        let prevHash = GetPreviousHash(block);
        let sig = GetQuantumSignature(block);
        let hash = GetHash(block);
        
        Message($"--- 区块 #{idx} ---");
        Message($"时间戳: {ts}");
        Message($"数据: {data}");
        Message($"前驱哈希: {prevHash}");
        Message($"量子签名: {sig}");
        Message($"区块哈希: {hash}");
    }

    @EntryPoint()
    operation Main() : Unit {
        Message("========================================");
        Message("   量子区块链核心模块测试");
        Message("========================================");
        Message("");
        
        Message("1. 创建创世区块...");
        let genesisBlock = CreateGenesisBlock();
        PrintBlock(genesisBlock);
        Message("");
        
        Message("2. 初始化区块链...");
        mutable chain = [genesisBlock];
        Message("");
        
        Message("3. 添加第一个区块...");
        set chain = AddBlock(chain, "Alice -> Bob: 10 QTC");
        Message("");
        
        Message("4. 添加第二个区块...");
        set chain = AddBlock(chain, "Bob -> Charlie: 5 QTC");
        Message("");
        
        Message("5. 添加第三个区块...");
        set chain = AddBlock(chain, "Charlie -> Dave: 3 QTC");
        Message("");
        
        Message("6. 区块链信息:");
        GetChainInfo(chain);
        Message("");
        
        Message("7. 验证区块链完整性...");
        let isValid = IsChainValid(chain);
        Message($"验证结果: {isValid}");
        Message("");
        
        Message("8. 打印所有区块:");
        for i in 0..Length(chain)-1 {
            PrintBlock(chain[i]);
            Message("");
        }
        
        Message("========================================");
        Message("   测试完成");
        Message("========================================");
    }
}
