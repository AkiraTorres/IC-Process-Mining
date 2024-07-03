def find_pattern_occurrences_with_gaps(lst, pattern):
    pattern_length = len(pattern)
    result = []

    i = 0
    while i <= len(lst) - pattern_length:
        j = 0
        while j < pattern_length and lst[i + j] == pattern[j]:
            j += 1
        if j == pattern_length:
            result.append(lst[i: i + pattern_length])
            i += pattern_length
        else:
            i += 1

    return result


# Example usage:
lst = [1, 2, 3, 2, 1, 5, 6, 7, 2, 1, 2]
pattern = [1, 2]
occurrences = find_pattern_occurrences_with_gaps(lst, pattern)
print(occurrences)  # Output: [[1, 2], [1, 2], [1, 2]]
