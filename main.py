import random
import sys

def find_moov_region(data):
    pos = data.find(b'moov')
    if pos == -1:
        return None
    if pos >= 4:
        moov_size = int.from_bytes(data[pos-4:pos], 'big')
        return (pos - 4, pos + moov_size)
    return (pos, pos + 10000)

# ========== BASE PATTERNS ==========

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

def glitch_shift(data, skip_header, moov_region):
    for i in range(skip_header, len(data) - 10, 500):
        if moov_region and moov_region[0] <= i < moov_region[1]:
            continue
        shift = random.randint(1, 5)
        if i + shift < len(data):
            data[i], data[i + shift] = data[i + shift], data[i]
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

# ========== NEW PATTERNS ==========

def glitch_noise(data, skip_header, intensity, moov_region):
    file_size = len(data)
    num_bursts = max(1, int(file_size * intensity * 0.5))
    for _ in range(num_bursts):
        pos = random.randint(skip_header, file_size - 100)
        if moov_region and moov_region[0] <= pos < moov_region[1]:
            continue
        burst_len = random.randint(10, 50)
        for i in range(burst_len):
            if pos + i < file_size:
                data[pos + i] = random.randint(0, 255)
    return data

def glitch_pixelate(data, skip_header, moov_region):
    for _ in range(10):
        pos = random.randint(skip_header, len(data) - 1000)
        if moov_region and moov_region[0] <= pos < moov_region[1]:
            continue
        block_size = random.randint(200, 800)
        pattern = data[pos:pos + 50]
        for i in range(0, block_size, 50):
            if pos + i + 50 < len(data):
                data[pos + i:pos + i + 50] = pattern
    return data

def glitch_scramble(data, skip_header, moov_region):
    for _ in range(5):
        start1 = random.randint(skip_header, len(data) - 1000)
        start2 = random.randint(skip_header, len(data) - 1000)
        if moov_region and (moov_region[0] <= start1 < moov_region[1] or moov_region[0] <= start2 < moov_region[1]):
            continue
        size = random.randint(100, 500)
        chunk1 = data[start1:start1 + size]
        chunk2 = data[start2:start2 + size]
        data[start1:start1 + size] = chunk2
        data[start2:start2 + size] = chunk1
    return data

def glitch_fade(data, skip_header, moov_region):
    file_size = len(data)
    intensity_start = 0.001
    intensity_end = 0.02
    for i in range(skip_header, file_size):
        if moov_region and moov_region[0] <= i < moov_region[1]:
            continue
        progress = (i - skip_header) / (file_size - skip_header)
        local_intensity = intensity_start + (intensity_end - intensity_start) * progress
        if random.random() < local_intensity:
            data[i] = random.randint(0, 255)
    return data

def glitch_strobe(data, skip_header, moov_region):
    file_size = len(data)
    section_size = 5000
    for section in range(skip_header, file_size, section_size):
        if random.random() > 0.5:
            continue
        for i in range(section, min(section + section_size, file_size)):
            if moov_region and moov_region[0] <= i < moov_region[1]:
                continue
            if random.random() < 0.3:
                data[i] = random.randint(0, 255)
    return data

def glitch_mirror(data, skip_header, moov_region):
    for _ in range(8):
        src = random.randint(skip_header, len(data) - 2000)
        dst = random.randint(skip_header, len(data) - 2000)
        if moov_region and (moov_region[0] <= src < moov_region[1] or moov_region[0] <= dst < moov_region[1]):
            continue
        size = random.randint(100, 400)
        if src + size < len(data) and dst + size < len(data):
            data[dst:dst + size] = data[src:src + size]
    return data

def glitch_delay(data, skip_header, moov_region):
    for _ in range(5):
        start = random.randint(skip_header, len(data) - 1000)
        if moov_region and moov_region[0] <= start < moov_region[1]:
            continue
        size = random.randint(200, 600)
        delay = random.randint(100, 300)
        chunk = data[start:start + size]
        insert_pos = min(start + delay, len(data) - size)
        if moov_region and moov_region[0] <= insert_pos < moov_region[1]:
            continue
        for j, b in enumerate(chunk):
            if insert_pos + j < len(data):
                data[insert_pos + j] = b
    return data

def glitch_distort(data, skip_header, moov_region):
    """Adds subtle distortion by slightly modifying byte values (not full flips)"""
    for i in range(skip_header, len(data)):
        if moov_region and moov_region[0] <= i < moov_region[1]:
            continue
        if random.random() < 0.01:  # 1% chance per byte
            # Add/subtract small amount (creates subtle distortion)
            data[i] = (data[i] + random.randint(-30, 30)) % 256
    return data

def glitch_mp4(input_file, output_file, pattern="random", intensity=0.005):
    with open(input_file, 'rb') as f:
        data = bytearray(f.read())
    
    file_size = len(data)
    skip_header = min(50000, int(file_size * 0.05))
    moov_region = find_moov_region(data)
    
    if moov_region:
        print(f"Found moov atom at {moov_region[0]}-{moov_region[1]} (protected)")
    print(f"File size: {file_size} bytes")
    print(f"Pattern: {pattern}, Intensity: {intensity*100}%")
    
    step = max(30, int(100 / intensity)) if pattern == "bitflip" else 47
    
    if pattern == "random":
        data = glitch_random(data, skip_header, intensity, moov_region)
    elif pattern == "bitflip":
        data = glitch_bitflip(data, skip_header, step, moov_region)
    elif pattern == "shift":
        data = glitch_shift(data, skip_header, moov_region)
    elif pattern == "duplicate":
        data = glitch_duplicate(data, skip_header, moov_region)
    elif pattern == "block":
        data = glitch_block(data, skip_header, moov_region)
    elif pattern == "rainbow":
        data = glitch_rainbow(data, skip_header, moov_region)
    elif pattern == "noise":
        data = glitch_noise(data, skip_header, intensity, moov_region)
    elif pattern == "pixelate":
        data = glitch_pixelate(data, skip_header, moov_region)
    elif pattern == "scramble":
        data = glitch_scramble(data, skip_header, moov_region)
    elif pattern == "fade":
        data = glitch_fade(data, skip_header, moov_region)
    elif pattern == "strobe":
        data = glitch_strobe(data, skip_header, moov_region)
    elif pattern == "mirror":
        data = glitch_mirror(data, skip_header, moov_region)
    elif pattern == "delay":
        data = glitch_delay(data, skip_header, moov_region)
    elif pattern == "distort":
        data = glitch_distort(data, skip_header, moov_region)
    elif pattern == "chaos":
        data = glitch_random(data, skip_header, intensity * 0.5, moov_region)
        data = glitch_noise(data, skip_header, intensity, moov_region)
        data = glitch_block(data, skip_header, moov_region)
        data = glitch_shift(data, skip_header, moov_region)
        data = glitch_duplicate(data, skip_header, moov_region)
        if random.random() > 0.5:
            data = glitch_scramble(data, skip_header, moov_region)
    elif pattern.startswith("custom:"):
        custom_patterns = pattern.split(":")[1].split(",")
        print(f"Custom patterns: {custom_patterns}")
        for p in custom_patterns:
            p = p.strip()
            if p == "random":
                data = glitch_random(data, skip_header, intensity, moov_region)
            elif p == "bitflip":
                data = glitch_bitflip(data, skip_header, step, moov_region)
            elif p == "shift":
                data = glitch_shift(data, skip_header, moov_region)
            elif p == "duplicate":
                data = glitch_duplicate(data, skip_header, moov_region)
            elif p == "block":
                data = glitch_block(data, skip_header, moov_region)
            elif p == "rainbow":
                data = glitch_rainbow(data, skip_header, moov_region)
            elif p == "noise":
                data = glitch_noise(data, skip_header, intensity, moov_region)
            elif p == "pixelate":
                data = glitch_pixelate(data, skip_header, moov_region)
            elif p == "scramble":
                data = glitch_scramble(data, skip_header, moov_region)
            elif p == "fade":
                data = glitch_fade(data, skip_header, moov_region)
            elif p == "strobe":
                data = glitch_strobe(data, skip_header, moov_region)
            elif p == "mirror":
                data = glitch_mirror(data, skip_header, moov_region)
            elif p == "delay":
                data = glitch_delay(data, skip_header, moov_region)
            elif p == "distort":
                data = glitch_distort(data, skip_header, moov_region)
    else:
        data = glitch_random(data, skip_header, intensity * 0.7, moov_region)
        data = glitch_block(data, skip_header, moov_region)
        data = glitch_duplicate(data, skip_header, moov_region)
    
    with open(output_file, 'wb') as f:
        f.write(data)
    
    print(f"Saved: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python main.py input.mp4 output.mp4 [pattern] [intensity]")
        print("\n===== PATTERNS =====")
        print("  random     - Random byte flips")
        print("  bitflip    - Regular pattern bit flips")
        print("  shift      - Byte shifting (warp effect)")
        print("  duplicate  - Frame duplication (stutter)")
        print("  block      - Solid color blocks")
        print("  rainbow    - Color shifting")
        print("  noise      - Bursts of random noise")
        print("  pixelate   - Repeating patterns (pixelation)")
        print("  scramble   - Swaps chunks of data")
        print("  fade       - Progressive damage (worse at the end)")
        print("  strobe     - Alternating clean/corrupted sections")
        print("  mirror     - Copies data from one area to another")
        print("  delay      - Shifted regions (echo/delay effect)")
        print("  distort    - Subtle distortion (slightly modified bytes)")
        print("  chaos      - EVERYTHING combined")
        print("\n===== CUSTOM =====")
        print("  custom:block,duplicate,noise")
        print("  custom:random,distort,rainbow")
        print("\nIntensity: 0.001 to 0.02 (default 0.005)")
        print("\nExamples:")
        print("  python main.py video.mp4 out.mp4 distort 0.005")
        print("  python main.py video.mp4 out.mp4 custom:block,duplicate,distort 0.004")
        print("  python main.py video.mp4 out.mp4 custom:random,noise,rainbow 0.003")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    pattern = sys.argv[3] if len(sys.argv) > 3 else "random"
    intensity = float(sys.argv[4]) if len(sys.argv) > 4 else 0.005
    
    glitch_mp4(input_file, output_file, pattern, intensity)
