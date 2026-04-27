import random
import sys

def find_protected_regions(data):
    """Find all regions that would break playback if corrupted"""
    protected_regions = []
    
    # Critical atoms
    markers = [b'moov', b'trak', b'mdia', b'minf', b'stbl', b'stsd', b'avc1', b'avcC', b'hdlr', b'soun']
    
    for marker in markers:
        pos = 0
        while True:
            pos = data.find(marker, pos)
            if pos == -1:
                break
            # Size is at pos-4
            if pos >= 4:
                size = int.from_bytes(data[pos-4:pos], 'big')
                start = pos - 4
                end = min(len(data), pos + size)
                protected_regions.append((start, end))
            else:
                protected_regions.append((pos, pos + 1000))
            pos = end if 'end' in locals() else pos + 1
    
    # Merge overlapping regions
    protected_regions.sort()
    merged = []
    for start, end in protected_regions:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    
    return merged

def is_protected(pos, protected_regions):
    for start, end in protected_regions:
        if start <= pos < end:
            return True
    return False

def glitch_random(data, skip_header, intensity, protected_regions):
    file_size = len(data)
    num_corrupt = max(1, int(file_size * intensity))
    corrupted = 0
    for _ in range(num_corrupt):
        pos = random.randint(skip_header, file_size - 1)
        if is_protected(pos, protected_regions):
            continue
        data[pos] = random.randint(0, 255)
        corrupted += 1
    print(f"  Corrupted {corrupted} bytes (skipped protected areas)")
    return data

def glitch_bitflip(data, skip_header, step, protected_regions):
    count = 0
    for i in range(skip_header, len(data), step):
        if is_protected(i, protected_regions):
            continue
        data[i] ^= 0xFF
        count += 1
    print(f"  Bitflipped {count} bytes")
    return data

def glitch_duplicate(data, skip_header, protected_regions):
    count = 0
    for _ in range(20):
        start = random.randint(skip_header, len(data) - 5000)
        if is_protected(start, protected_regions):
            continue
        length = random.randint(300, 1000)
        chunk = data[start:start + length]
        insert_pos = random.randint(skip_header, len(data) - 1)
        if is_protected(insert_pos, protected_regions):
            continue
        for j, b in enumerate(chunk):
            if insert_pos + j < len(data):
                data[insert_pos + j] = b
        count += 1
    print(f"  Duplicated {count} chunks")
    return data

def glitch_block(data, skip_header, protected_regions):
    count = 0
    for _ in range(10):
        pos = random.randint(skip_header, len(data) - 5000)
        if is_protected(pos, protected_regions):
            continue
        block_size = random.randint(200, 800)
        fill_byte = random.randint(0, 255)
        for i in range(block_size):
            if pos + i < len(data):
                data[pos + i] = fill_byte
        count += 1
    print(f"  Added {count} blocks")
    return data

def glitch_rainbow(data, skip_header, protected_regions):
    count = 0
    for i in range(skip_header, len(data)):
        if i % 3 == 0 and not is_protected(i, protected_regions):
            data[i] = (data[i] + 30) % 256
            count += 1
    print(f"  Rainbow shifted {count} bytes")
    return data

def glitch_mp4(input_file, output_file, pattern="random", intensity=0.003):
    with open(input_file, 'rb') as f:
        data = bytearray(f.read())
    
    file_size = len(data)
    skip_header = min(100000, int(file_size * 0.05))
    protected_regions = find_protected_regions(data)
    
    print(f"File: {input_file} ({file_size:,} bytes)")
    print(f"Protected regions: {len(protected_regions)}")
    print(f"Pattern: {pattern}, Intensity: {intensity*100}%")
    
    step = max(50, int(100 / intensity)) if pattern == "bitflip" else 47
    
    if pattern == "random":
        data = glitch_random(data, skip_header, intensity, protected_regions)
    elif pattern == "bitflip":
        data = glitch_bitflip(data, skip_header, step, protected_regions)
    elif pattern == "duplicate":
        data = glitch_duplicate(data, skip_header, protected_regions)
    elif pattern == "block":
        data = glitch_block(data, skip_header, protected_regions)
    elif pattern == "rainbow":
        data = glitch_rainbow(data, skip_header, protected_regions)
    else:
        data = glitch_random(data, skip_header, intensity * 0.7, protected_regions)
        data = glitch_block(data, skip_header, protected_regions)
    
    with open(output_file, 'wb') as f:
        f.write(data)
    
    print(f"Saved: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python main.py input.mp4 output.mp4 [pattern] [intensity]")
        print("\nIntensity: 0.001 to 0.02 (lower = safer for mobile)")
        print("Recommended for TikTok/mobile: 0.002 to 0.004")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    pattern = sys.argv[3] if len(sys.argv) > 3 else "random"
    intensity = float(sys.argv[4]) if len(sys.argv) > 4 else 0.003
    
    glitch_mp4(input_file, output_file, pattern, intensity)
