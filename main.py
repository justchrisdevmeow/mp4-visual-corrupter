import random
import sys

def glitch_mp4(input_file, output_file, pattern="random", intensity=0.003):
    with open(input_file, 'rb') as f:
        data = bytearray(f.read())
    
    file_size = len(data)
    
    # Hardcoded safe zone: first 150KB (covers moov and most headers)
    safe_zone = min(150000, int(file_size * 0.15))
    
    print(f"File: {input_file} ({file_size:,} bytes)")
    print(f"Safe zone: first {safe_zone} bytes (protected)")
    print(f"Pattern: {pattern}, Intensity: {intensity*100}%")
    
    # Number of bytes to corrupt
    num_corrupt = max(1, int(file_size * intensity))
    print(f"Corrupting {num_corrupt} random bytes")
    
    if pattern == "random":
        for _ in range(num_corrupt):
            pos = random.randint(safe_zone, file_size - 1)
            data[pos] = random.randint(0, 255)
    
    elif pattern == "bitflip":
        step = max(50, int(200 / intensity))
        for i in range(safe_zone, len(data), step):
            data[i] ^= 0xFF
    
    elif pattern == "block":
        num_blocks = max(1, int(intensity * 100))
        for _ in range(num_blocks):
            pos = random.randint(safe_zone, file_size - 5000)
            block_size = random.randint(100, 500)
            fill_byte = random.randint(0, 255)
            for i in range(block_size):
                if pos + i < len(data):
                    data[pos + i] = fill_byte
    
    elif pattern == "duplicate":
        num_dup = max(1, int(intensity * 50))
        for _ in range(num_dup):
            start = random.randint(safe_zone, file_size - 3000)
            length = random.randint(200, 800)
            chunk = data[start:start + length]
            insert_pos = random.randint(safe_zone, file_size - 1)
            for j, b in enumerate(chunk):
                if insert_pos + j < len(data):
                    data[insert_pos + j] = b
    
    elif pattern == "rainbow":
        for i in range(safe_zone, len(data)):
            if i % 3 == 0:
                data[i] = (data[i] + 30) % 256
    
    else:  # default random
        for _ in range(num_corrupt):
            pos = random.randint(safe_zone, file_size - 1)
            data[pos] = random.randint(0, 255)
    
    with open(output_file, 'wb') as f:
        f.write(data)
    
    print(f"Saved: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python main.py input.mp4 output.mp4 [pattern] [intensity]")
        print("Patterns: random, bitflip, block, duplicate, rainbow")
        print("Intensity: 0.001 to 0.02 (default 0.003)")
        print("\nFor TikTok/mobile: use 0.002 to 0.004")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    pattern = sys.argv[3] if len(sys.argv) > 3 else "random"
    intensity = float(sys.argv[4]) if len(sys.argv) > 4 else 0.003
    
    glitch_mp4(input_file, output_file, pattern, intensity)
