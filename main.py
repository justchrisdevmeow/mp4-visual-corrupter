import random
import sys

def glitch_random(data, skip_header, audio_regions, intensity):
    num_corrupt = max(1, int(len(data) / 10000 * intensity * 3))
    for _ in range(num_corrupt):
        pos = random.randint(skip_header, len(data) - 1)
        # Corrupt audio but less aggressively
        is_audio = any(start <= pos < end for start, end in audio_regions)
        if is_audio and random.random() > 0.3:  # 70% chance to still corrupt audio
            data[pos] = random.randint(0, 255)
        elif not is_audio:
            data[pos] = random.randint(0, 255)
    return data

def glitch_bitflip(data, skip_header, audio_regions, intensity):
    step = max(10, int(1500 / intensity))
    for i in range(skip_header, len(data), step):
        is_audio = any(start <= i < end for start, end in audio_regions)
        if is_audio and random.random() > 0.4:  # 60% chance
            data[i] ^= 0xFF
        elif not is_audio:
            data[i] ^= 0xFF
    return data

def glitch_block(data, skip_header, audio_regions, intensity):
    num_blocks = max(1, int(intensity * 1.5))
    for _ in range(num_blocks):
        pos = random.randint(skip_header, len(data) - 2000)
        is_audio = any(start <= pos < end for start, end in audio_regions)
        if is_audio and random.random() > 0.5:  # 50% chance
            block_size = random.randint(20, 80)  # Smaller blocks in audio
            fill_byte = random.randint(0, 255)
            for i in range(block_size):
                if pos + i < len(data):
                    data[pos + i] = fill_byte
        elif not is_audio:
            block_size = random.randint(50, 200)
            fill_byte = random.randint(0, 255)
            for i in range(block_size):
                if pos + i < len(data):
                    data[pos + i] = fill_byte
    return data

def glitch_duplicate(data, skip_header, audio_regions, intensity):
    num_dup = max(1, int(intensity * 1.2))
    for _ in range(num_dup):
        # Find position (audio or video)
        start = random.randint(skip_header, len(data) - 2000)
        length = random.randint(100, 400)
        chunk = data[start:start + length]
        insert_pos = random.randint(skip_header, len(data) - 1)
        for j, b in enumerate(chunk):
            if insert_pos + j < len(data):
                data[insert_pos + j] = b
    return data

def glitch_rainbow(data, skip_header, audio_regions, intensity):
    step = max(5, int(150 / intensity))
    for i in range(skip_header, len(data)):
        if i % step == 0:
            is_audio = any(start <= i < end for start, end in audio_regions)
            if not is_audio or random.random() > 0.6:  # 40% chance for audio color shift
                data[i] = (data[i] + random.randint(1, 20)) % 256
    return data

def find_audio_regions(data):
    """Find audio track areas in MP4"""
    regions = []
    audio_markers = [b'moov', b'trak', b'mdia', b'hdlr', b'soun']
    for marker in audio_markers:
        pos = 0
        while True:
            pos = data.find(marker, pos)
            if pos == -1:
                break
            start = max(0, pos - 300)
            end = min(len(data), pos + 800)
            regions.append((start, end))
            pos = end
    # Merge overlapping regions
    regions.sort()
    merged = []
    for start, end in regions:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged

def glitch_mp4(input_file, output_file, pattern="custom", intensity=10, custom_patterns=None):
    with open(input_file, 'rb') as f:
        data = bytearray(f.read())
    
    file_size = len(data)
    skip_header = min(50000, int(file_size * 0.05))
    
    audio_regions = find_audio_regions(data)
    
    print(f"File: {input_file} ({file_size} bytes)")
    print(f"Pattern: {pattern}, Intensity: {intensity}")
    print(f"Audio regions: {len(audio_regions)}")
    
    if pattern == "random":
        data = glitch_random(data, skip_header, audio_regions, intensity)
    elif pattern == "bitflip":
        data = glitch_bitflip(data, skip_header, audio_regions, intensity)
    elif pattern == "block":
        data = glitch_block(data, skip_header, audio_regions, intensity)
    elif pattern == "duplicate":
        data = glitch_duplicate(data, skip_header, audio_regions, intensity)
    elif pattern == "rainbow":
        data = glitch_rainbow(data, skip_header, audio_regions, intensity)
    elif pattern == "custom" and custom_patterns:
        for p in custom_patterns:
            if p == "random":
                data = glitch_random(data, skip_header, audio_regions, intensity // 2)
            elif p == "bitflip":
                data = glitch_bitflip(data, skip_header, audio_regions, intensity // 2)
            elif p == "block":
                data = glitch_block(data, skip_header, audio_regions, intensity // 2)
            elif p == "duplicate":
                data = glitch_duplicate(data, skip_header, audio_regions, intensity // 2)
            elif p == "rainbow":
                data = glitch_rainbow(data, skip_header, audio_regions, intensity // 2)
    else:
        # Default: block + duplicate (safe but visible)
        data = glitch_block(data, skip_header, audio_regions, intensity // 2)
        data = glitch_duplicate(data, skip_header, audio_regions, intensity // 2)
    
    with open(output_file, 'wb') as f:
        f.write(data)
    
    print(f"Saved: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python main.py input.mp4 output.mp4 [pattern] [intensity] [custom:pattern,pattern]")
        print("\nPatterns: random, bitflip, block, duplicate, rainbow, custom")
        print("Example: python main.py video.mp4 out.mp4 custom 10 block,duplicate")
        print("\nIntensity 1-30:")
        print("  5 = light glitches, audio pops occasionally")
        print("  10 = noticeable glitches, audio stutters")
        print("  15 = heavy glitches, audio warped")
        print("  20 = extreme, audio glitchy but still plays")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if len(sys.argv) > 3:
        pattern = sys.argv[3]
    else:
        pattern = "custom"
    
    if len(sys.argv) > 4:
        intensity = int(sys.argv[4])
    else:
        intensity = 10
    
    custom_patterns = None
    if len(sys.argv) > 5 and pattern == "custom":
        custom_patterns = sys.argv[5].split(",")
    
    glitch_mp4(input_file, output_file, pattern, intensity, custom_patterns)
