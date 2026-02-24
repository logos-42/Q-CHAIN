namespace QuantumBlockchain.QEC {
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Measurement;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Arrays;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Logical;

    newtype SurfaceCodeConfig = (
        distance: Int,
        dataQubits: Qubit[],
        stabilizerQubits: Qubit[]
    );

    function GetSurfaceCodeDistance(config : SurfaceCodeConfig) : Int {
        let (d, _, _) = config!;
        return d;
    }

    function GetSurfaceCodeDataQubits(config : SurfaceCodeConfig) : Qubit[] {
        let (_, data, _) = config!;
        return data;
    }

    function GetSurfaceCodeStabilizerQubits(config : SurfaceCodeConfig) : Qubit[] {
        let (_, _, stab) = config!;
        return stab;
    }

    operation EncodeShorCode(logicalQubit : Qubit) : Qubit[] {
        let physicalQubits = new Qubit[9];

        for i in 0..8 {
            set physicalQubits[i] = Qubit();
        }

        CNOT(logicalQubit, physicalQubits[0]);
        CNOT(logicalQubit, physicalQubits[1]);
        CNOT(logicalQubit, physicalQubits[2]);

        CNOT(physicalQubits[0], physicalQubits[3]);
        CNOT(physicalQubits[0], physicalQubits[4]);
        CNOT(physicalQubits[1], physicalQubits[4]);
        CNOT(physicalQubits[1], physicalQubits[5]);
        CNOT(physicalQubits[2], physicalQubits[6]);
        CNOT(physicalQubits[2], physicalQubits[7]);

        CNOT(physicalQubits[3], physicalQubits[6]);
        CNOT(physicalQubits[3], physicalQubits[7]);
        CNOT(physicalQubits[4], physicalQubits[7]);
        CNOT(physicalQubits[4], physicalQubits[8]);
        CNOT(physicalQubits[5], physicalQubits[8]);

        H(physicalQubits[0]);
        H(physicalQubits[1]);
        H(physicalQubits[2]);
        H(physicalQubits[3]);
        H(physicalQubits[6]);

        CNOT(physicalQubits[0], physicalQubits[3]);
        CNOT(physicalQubits[1], physicalQubits[4]);
        CNOT(physicalQubits[2], physicalQubits[5]);
        CNOT(physicalQubits[3], physicalQubits[6]);
        CNOT(physicalQubits[4], physicalQubits[7]);
        CNOT(physicalQubits[5], physicalQubits[8]);

        return physicalQubits;
    }

    operation DecodeShorCode(physicalQubits : Qubit[]) : Qubit {
        let logicalQubit = Qubit();

        CNOT(physicalQubits[0], physicalQubits[3]);
        CNOT(physicalQubits[1], physicalQubits[4]);
        CNOT(physicalQubits[2], physicalQubits[5]);
        CNOT(physicalQubits[3], physicalQubits[6]);
        CNOT(physicalQubits[4], physicalQubits[7]);
        CNOT(physicalQubits[5], physicalQubits[8]);

        H(physicalQubits[0]);
        H(physicalQubits[1]);
        H(physicalQubits[2]);
        H(physicalQubits[3]);
        H(physicalQubits[6]);

        CNOT(physicalQubits[0], logicalQubit);
        CNOT(physicalQubits[1], logicalQubit);
        CNOT(physicalQubits[2], logicalQubit);

        return logicalQubit;
    }

    operation MeasureShorSyndrome(physicalQubits : Qubit[]) : Int[] {
        mutable syndrome = new Int[8];

        let a0 = M(physicalQubits[0]);
        let a1 = M(physicalQubits[1]);
        let a2 = M(physicalQubits[2]);
        let b0 = M(physicalQubits[3]);
        let b1 = M(physicalQubits[4]);
        let b2 = M(physicalQubits[5]);
        let c0 = M(physicalQubits[6]);
        let c1 = M(physicalQubits[7]);
        let c2 = M(physicalQubits[8]);

        set syndrome[0] = (BoolAsInt(a0 == One) + BoolAsInt(a1 == One) + BoolAsInt(a2 == One)) % 2;
        set syndrome[1] = (BoolAsInt(b0 == One) + BoolAsInt(b1 == One) + BoolAsInt(b2 == One)) % 2;
        set syndrome[2] = (BoolAsInt(c0 == One) + BoolAsInt(c1 == One) + BoolAsInt(c2 == One)) % 2;
        set syndrome[3] = (BoolAsInt(a0 == One) + BoolAsInt(b0 == One) + BoolAsInt(c0 == One)) % 2;
        set syndrome[4] = (BoolAsInt(a1 == One) + BoolAsInt(b1 == One) + BoolAsInt(c1 == One)) % 2;
        set syndrome[5] = (BoolAsInt(a2 == One) + BoolAsInt(b2 == One) + BoolAsInt(c2 == One)) % 2;
        set syndrome[6] = (BoolAsInt(b0 == One) + BoolAsInt(b1 == One) + BoolAsInt(b2 == One)) % 2;
        set syndrome[7] = (BoolAsInt(c0 == One) + BoolAsInt(c1 == One) + BoolAsInt(c2 == One)) % 2;

        return syndrome;
    }

    operation CorrectShorCode(physicalQubits : Qubit[]) : Unit {
        let syndrome = MeasureShorSyndrome(physicalQubits);

        if (syndrome[0] == 1) {
            X(physicalQubits[0]);
        }
        if (syndrome[1] == 1) {
            X(physicalQubits[1]);
        }
        if (syndrome[2] == 1) {
            X(physicalQubits[2]);
        }
        if (syndrome[3] == 1) {
            Z(physicalQubits[0]);
        }
        if (syndrome[4] == 1) {
            Z(physicalQubits[1]);
        }
        if (syndrome[5] == 1) {
            Z(physicalQubits[2]);
        }

        let bitSyndrome = syndrome[6] * 4 + syndrome[7] * 2 + syndrome[0] + syndrome[1] * 2 + syndrome[2] * 4;
        
        if (bitSyndrome == 1 or bitSyndrome == 7) {
            X(physicalQubits[3]);
        }
        elif (bitSyndrome == 2 or bitSyndrome == 6) {
            X(physicalQubits[4]);
        }
        elif (bitSyndrome == 3) {
            X(physicalQubits[5]);
        }
        elif (bitSyndrome == 4 or bitSyndrome == 5) {
            X(physicalQubits[6]);
        }

        let phaseSyndrome = syndrome[3] * 4 + syndrome[4] * 2 + syndrome[5];
        
        if (phaseSyndrome == 1 or phaseSyndrome == 7) {
            Z(physicalQubits[3]);
        }
        elif (phaseSyndrome == 2 or phaseSyndrome == 6) {
            Z(physicalQubits[4]);
        }
        elif (phaseSyndrome == 3) {
            Z(physicalQubits[5]);
        }
        elif (phaseSyndrome == 4 or phaseSyndrome == 5) {
            Z(physicalQubits[6]);
        }
    }

    operation CreateSurfaceCode(distance : Int) : (Qubit[], Int) {
        let nDataQubits = distance * distance;
        let nStabilizerQubits = (distance - 1) * (distance - 1);
        let totalQubits = nDataQubits + nStabilizerQubits;

        mutable dataQubits = new Qubit[nDataQubits];
        mutable stabilizerQubits = new Qubit[nStabilizerQubits];

        for i in 0..nDataQubits - 1 {
            set dataQubits[i] = Qubit();
        }
        for i in 0..nStabilizerQubits - 1 {
            set stabilizerQubits[i] = Qubit();
        }

        return (dataQubits + stabilizerQubits, distance);
    }

    operation EncodeInSurfaceCode(dataQubit : Qubit, surfaceQubits : Qubit[]) : Unit {
        let n = Length(surfaceQubits) - 1;
        let distance = 3;
        let nDataQubits = distance * distance;

        for i in 0..nDataQubits - 1 {
            CNOT(dataQubit, surfaceQubits[i]);
        }
    }

    operation MeasureSurfaceStabilizers(surfaceQubits : Qubit[], distance : Int) : Int[] {
        let nDataQubits = distance * distance;
        let nStabilizerQubits = (distance - 1) * (distance - 1);
        
        mutable syndrome = new Int[nStabilizerQubits];

        for i in 0..nStabilizerQubits - 1 {
            let stabQubitIdx = nDataQubits + i;
            
            let row = i / (distance - 1);
            let col = i % (distance - 1);
            
            let d1 = row * distance + col;
            let d2 = row * distance + col + 1;
            let d3 = (row + 1) * distance + col;
            let d4 = (row + 1) * distance + col + 1;

            CNOT(surfaceQubits[d1], surfaceQubits[stabQubitIdx]);
            CNOT(surfaceQubits[d2], surfaceQubits[stabQubitIdx]);
            CNOT(surfaceQubits[d3], surfaceQubits[stabQubitIdx]);
            CNOT(surfaceQubits[d4], surfaceQubits[stabQubitIdx]);

            let result = M(surfaceQubits[stabQubitIdx]);
            set syndrome[i] = BoolAsInt(result == One);

            Reset(surfaceQubits[stabQubitIdx]);
        }

        return syndrome;
    }

    operation DecodeFromSurfaceCode(surfaceQubits : Qubit[]) : Qubit {
        let logicalQubit = Qubit();
        let distance = 3;
        let nDataQubits = distance * distance;

        for i in 0..nDataQubits - 1 {
            CNOT(surfaceQubits[i], logicalQubit);
        }

        return logicalQubit;
    }

    operation EncodeBitFlip(logicalQubit : Qubit) : Qubit[] {
        let physicalQubits = new Qubit[3];

        for i in 0..2 {
            set physicalQubits[i] = Qubit();
        }

        CNOT(logicalQubit, physicalQubits[0]);
        CNOT(logicalQubit, physicalQubits[1]);
        CNOT(logicalQubit, physicalQubits[2]);

        return physicalQubits;
    }

    operation MeasureSyndrome(physicalQubits : Qubit[]) : Int[] {
        let syndrome0 = M(physicalQubits[0]);
        let syndrome1 = M(physicalQubits[1]);
        let syndrome2 = M(physicalQubits[2]);

        mutable errorPattern = 0;

        if (syndrome0 != syndrome1) {
            set errorPattern = errorPattern + 1;
        }
        if (syndrome0 != syndrome2) {
            set errorPattern = errorPattern + 2;
        }
        if (syndrome1 != syndrome2) {
            set errorPattern = errorPattern + 4;
        }

        return [errorPattern];
    }

    operation CorrectBitFlip(physicalQubits : Qubit[]) : Unit {
        let syndrome = MeasureSyndrome(physicalQubits);
        let errorPattern = syndrome[0];

        if (errorPattern == 1) {
            X(physicalQubits[0]);
        }
        elif (errorPattern == 2) {
            X(physicalQubits[1]);
        }
        elif (errorPattern == 3 or errorPattern == 4) {
            X(physicalQubits[2]);
        }
    }

    operation EncodePhaseFlip(logicalQubit : Qubit) : Qubit[] {
        let physicalQubits = new Qubit[3];

        for i in 0..2 {
            set physicalQubits[i] = Qubit();
        }

        H(physicalQubits[0]);
        H(physicalQubits[1]);
        H(physicalQubits[2]);

        CNOT(logicalQubit, physicalQubits[0]);
        CNOT(logicalQubit, physicalQubits[1]);
        CNOT(logicalQubit, physicalQubits[2]);

        return physicalQubits;
    }

    operation MeasurePhaseSyndrome(physicalQubits : Qubit[]) : Int[] {
        mutable syndrome = new Int[2];

        H(physicalQubits[0]);
        H(physicalQubits[1]);
        H(physicalQubits[2]);

        let s0 = M(physicalQubits[0]);
        let s1 = M(physicalQubits[1]);
        let s2 = M(physicalQubits[2]);

        set syndrome[0] = BoolAsInt(s0 != s2);
        set syndrome[1] = BoolAsInt(s1 != s2);

        return syndrome;
    }

    operation CorrectPhaseFlip(physicalQubits : Qubit[]) : Unit {
        let syndrome = MeasurePhaseSyndrome(physicalQubits);

        if (syndrome[0] == 1) {
            Z(physicalQubits[0]);
        }
        if (syndrome[1] == 1) {
            Z(physicalQubits[1]);
        }
    }

    operation ApplyRandomError(qubits : Qubit[], errorProb : Double) : Unit {
        for i in 0..Length(qubits) - 1 {
            if (Random([errorProb, 1.0 - errorProb]) == 0) {
                let errorType = Random([0.33, 0.33, 0.34]);
                if (errorType == 0) {
                    X(qubits[i]);
                }
                elif (errorType == 1) {
                    Z(qubits[i]);
                }
                else {
                    Y(qubits[i]);
                }
            }
        }
    }

    operation ApplyBitFlipError(qubit : Qubit, prob : Double) : Unit {
        if (Random([prob, 1.0 - prob]) == 0) {
            X(qubit);
        }
    }

    operation ApplyPhaseError(qubit : Qubit, prob : Double) : Unit {
        if (Random([prob, 1.0 - prob]) == 0) {
            Z(qubit);
        }
    }

    operation ApplyDepolarizingError(qubit : Qubit, prob : Double) : Unit {
        let r = Random([prob / 3.0, prob / 3.0, prob / 3.0, 1.0 - prob]);
        if (r == 0) {
            X(qubit);
        }
        elif (r == 1) {
            Z(qubit);
        }
        elif (r == 2) {
            Y(qubit);
        }
    }

    operation VerifyErrorCorrection(original : Qubit, corrected : Qubit) : Bool {
        let resultOriginal = M(original);
        let resultCorrected = M(corrected);

        Reset(original);
        Reset(corrected);

        return resultOriginal == resultCorrected;
    }

    operation CalculateErrorRate(numTrials : Int, errorProb : Double) : Double {
        mutable errors = 0;

        for trial in 0..numTrials - 1 {
            let original = Qubit();
            H(original);

            let encoded = EncodeBitFlip(original);
            ApplyBitFlipError(encoded[0], errorProb);
            ApplyBitFlipError(encoded[1], errorProb);
            ApplyBitFlipError(encoded[2], errorProb);

            CorrectBitFlip(encoded);
            
            let decoded = Qubit();
            CNOT(encoded[0], decoded);
            CNOT(encoded[1], decoded);
            CNOT(encoded[2], decoded);

            let originalState = M(original);
            let decodedState = M(decoded);

            if (originalState != decodedState) {
                set errors = errors + 1;
            }

            Reset(original);
            for i in 0..2 {
                Reset(encoded[i]);
            }
            Reset(decoded);
        }

        return IntAsDouble(errors) / IntAsDouble(numTrials);
    }

    operation TestShorCode() : Bool {
        let original = Qubit();
        H(original);

        let encoded = EncodeShorCode(original);
        
        ApplyBitFlipError(encoded[4], 0.5);
        
        CorrectShorCode(encoded);
        
        let decoded = DecodeShorCode(encoded);
        
        let result = VerifyErrorCorrection(original, decoded);

        Reset(original);
        for i in 0..8 {
            Reset(encoded[i]);
        }
        Reset(decoded);

        return result;
    }

    operation TestBitFlipCode() : Bool {
        let original = Qubit();
        H(original);

        let encoded = EncodeBitFlip(original);
        
        ApplyBitFlipError(encoded[1], 0.5);
        
        CorrectBitFlip(encoded);
        
        let decoded = Qubit();
        CNOT(encoded[0], decoded);
        CNOT(encoded[1], decoded);
        CNOT(encoded[2], decoded);
        
        let result = VerifyErrorCorrection(original, decoded);

        Reset(original);
        for i in 0..2 {
            Reset(encoded[i]);
        }
        Reset(decoded);

        return result;
    }

    operation TestPhaseFlipCode() : Bool {
        let original = Qubit();
        H(original);

        let encoded = EncodePhaseFlip(original);
        
        ApplyPhaseError(encoded[1], 0.5);
        
        CorrectPhaseFlip(encoded);
        
        let decoded = Qubit();
        for i in 0..2 {
            H(encoded[i]);
        }
        CNOT(encoded[0], decoded);
        CNOT(encoded[1], decoded);
        CNOT(encoded[2], decoded);
        
        let result = VerifyErrorCorrection(original, decoded);

        Reset(original);
        for i in 0..2 {
            Reset(encoded[i]);
        }
        Reset(decoded);

        return result;
    }

    operation DemoQuantumErrorCorrection() : Unit {
        Message("========================================");
        Message("Quantum Error Correction Demo - PQEC");
        Message("========================================");

        Message("\n--- Testing Bit-Flip Code ---");
        let bitFlipResult = TestBitFlipCode();
        Message($"Bit-Flip Code Test: {bitFlipResult}");

        Message("\n--- Testing Phase-Flip Code ---");
        let phaseFlipResult = TestPhaseFlipCode();
        Message($"Phase-Flip Code Test: {phaseFlipResult}");

        Message("\n--- Testing Shor Code ---");
        let shorResult = TestShorCode();
        Message($"Shor Code Test: {shorResult}");

        Message("\n--- Error Rate Analysis ---");
        let errorRate = CalculateErrorRate(100, 0.1);
        Message($"Error Rate with 10% error probability: {errorRate * 100.0}%");

        let improvedErrorRate = CalculateErrorRate(100, 0.05);
        Message($"Error Rate with 5% error probability: {improvedErrorRate * 100.0}%");

        Message("\n========================================");
        Message("Quantum Error Correction Demo Complete");
        Message("========================================");
    }

    @EntryPoint()
    operation Main() : Unit {
        DemoQuantumErrorCorrection();
    }
}
