import random
import sys

def find_moov_region(data):
    """Find the moov atom and return its start and end positions"""
    pos = data.find(b'moov')
    if pos == -1:
        return None
    # Moov atom size is at pos-4
    if pos >= 4:
        moov_size = int.from_bytes(data[pos-4:pos], 'big')
        return (pos - 4, pos + moov_size)
    return (pos, pos + 10000)

def glitch_random(data, skip_header, intensity, moov_region):
    file_size = len(data)
    num_corrupt = max(1, int(file_size * intensity))
    for _ in range(num_corrupt):
        pos = random.randint(skip_header, file_size - 1)
        if moov_region and moov_region[0] <= pos < moov_region[1]:
            continue
        data[pos] = random.randint(0, 255)
    return data

def glitch_bitflip(data, skip_header, step, moov_region):
    for i in range(skip_header, len(data), step):
        if moov_region and moov_region[0] <= i < moov_region[1]:
            continue
        data[i] ^= 0xFF
    return data

def glitch_duplicate(data, skip_header, moov_region):
    for _ in range(30):
        start = random.randint(skip_header, len(data) - 2000)
        if moov_region and moov_region[0] <= start < moov_region[1]:
            continue
        length = random.randint(200, 800)
        chunk = data[start:start + length]
        insert_pos = random.randint(skip_header, len(data) - 1)
        if moov_region and moov_region[0] <= insert_pos < moov_region[1]:
            continue
        for j, b in enumerate(chunk):
            if insert_pos + j < len(data):
                data[insert_pos + j] = b
    return data

def glitch_block(data, skip_header, moov_region):
    for _ in range(15):
        pos = random.randint(skip_header, len(data) - 2000)
        if moov_region and moov_region[0] <= pos < moov_region[1]:
            continue
        block_size = random.randint(100, 500)
        fill_byte = random.randint(0, 255)
        for i in range(block_size):
            if pos + i < len(data):
                data[pos + i] = fill_byte
    return data

def glitch_rainbow(data, skip_header, moov_region):
    for i in range(skip_header, len(data)):
        if i % 3 == 0:
            if moov_region and moov_region[0] <= i < moov_region[1]:
                continue
            data[i] = (data[i] + 30) % 256
    return data

def glitch_mp4(input_file, output_file, pattern="random", intensity=0.005):
    with open(input_file, 'rb') as f:
        data = bytearray(f.read())
    
    file_size = len(data)
    skip_header = min(50000, int(file_size * 0.05))
    moov_region = find_moov_region(data)
    
    if moov_region:
        print(f"Found moov atom at {moov_region[0]}-{moov_region[1]} (protected)")
    else:
        print("No moov atom found")
    
    print(f"File size: {file_size} bytes")
    print(f"Pattern: {pattern}, Intensity: {intensity*100}%")
    
    step = max(30, int(100 / intensity)) if pattern == "bitflip" else 47
    
    if pattern == "random":
        data = glitch_random(data, skip_header, intensity, moov_region)
    elif pattern == "bitflip":
        data = glitch_bitflip(data, skip_header, step, moov_region)
    elif pattern == "duplicate":
        data = glitch_duplicate(data, skip_header, moov_region)
    elif pattern == "block":
        data = glitch_block(data, skip_header, moov_region)
    elif pattern == "rainbow":
        data = glitch_rainbow(data, skip_header, moov_region)
    else:
        # Default: random + block + duplicate (safe combo)
        data = glitch_random(data, skip_header, intensity * 0.7, moov_region)
        data = glitch_block(data, skip_header, moov_region)
        data = glitch_duplicate(data, skip_header, moov_region)
    
    with open(output_file, 'wb') as f:
        f.write(data)
    
    print(f"Saved: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python main.py input.mp4 output.mp4 [pattern] [intensity]")
        print("\nPatterns: random, bitflip, duplicate, block, rainbow")
        print("Intensity: 0.001 to 0.02 (default 0.005)")
        print("\nFor TikTok/mobile: use 'random' or 'block' with intensity 0.003-0.005")
        print("\nExamples:")
        print("  python main.py video.mp4 out.mp4 random 0.003")
        print("  python main.py video.mp4 out.mp4 block 0.004")
        print("  python main.py video.mp4 out.mp4 random 0.002")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    pattern = sys.argv[3] if len(sys.argv) > 3 else "random"
    intensity = float(sys.argv[4]) if len(sys.argv) > 4 else 0.005
    
    glitch_mp4(input_file, output_file, pattern, intensity)
