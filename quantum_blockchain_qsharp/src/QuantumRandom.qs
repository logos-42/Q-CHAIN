namespace QuantumBlockchain.QRNG {
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Measurement;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Arrays;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Canon;

    operation GenerateRandomBits(nBits : Int) : Result[] {
        mutable randomBits = new Result[0];
        let chunkSize = 16;
        
        let fullChunks = nBits / chunkSize;
        let remainder = nBits % chunkSize;
        
        for chunk in 0..fullChunks-1 {
            use qubits = Qubit[chunkSize];
            ApplyToEach(H, qubits);
            for i in 0..chunkSize-1 {
                let result = M(qubits[i]);
                set randomBits += [result];
            }
            ResetAll(qubits);
        }
        
        if remainder > 0 {
            use remainingQubits = Qubit[remainder];
            ApplyToEach(H, remainingQubits);
            for i in 0..remainder-1 {
                let result = M(remainingQubits[i]);
                set randomBits += [result];
            }
            ResetAll(remainingQubits);
        }
        
        return randomBits;
    }

    function BitStringToHex(bitArray : Result[]) : String {
        let numBytes = Length(bitArray) / 4;
        mutable hexString = "";
        
        for i in 0..numBytes-1 {
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

    operation GenerateQuantumSignature() : String {
        let signatureBits = 256;
        let randomBits = GenerateRandomBits(signatureBits);
        return BitStringToHex(randomBits);
    }

    @EntryPoint()
    operation Main() : Unit {
        Message("=== 量子随机数生成器测试 ===");
        Message("");
        
        let testBits = 32;
        Message($"生成 {testBits} 位随机比特...");
        let randomBits = GenerateRandomBits(testBits);
        
        mutable bitString = "";
        for bit in randomBits {
            set bitString += $"{ResultAsInt(bit)}";
        }
        Message($"随机比特串: {bitString}");
        
        let hexResult = BitStringToHex(randomBits);
        Message($"十六进制: {hexResult}");
        Message("");
        
        Message("生成量子签名 (256位)...");
        let signature = GenerateQuantumSignature();
        Message($"量子签名: {signature}");
        Message($"签名长度: {Length(signature)} 字符");
        Message("");
        
        Message("=== 测试完成 ===");
    }
}
