# from prefixspan import PrefixSpan
# import pandas as pd
#
# # Example sequence database with IDs
# data = [
#     (1, ["a", "b", "c", "a"]),
#     (2, ["a", "c", "b", "a"]),
#     (3, ["a", "b", "a", "b"]),
#     (4, ["a", "c", "c", "a"]),
#     (5, ["b", "a", "c", "b"]),
# ]
#
# # Convert the sequence database to the format required by PrefixSpan
# sequence_db = [seq for _, seq in data]
#
# # Apply PrefixSpan algorithm with a minimum support of 2
# ps = PrefixSpan(sequence_db)
# results = ps.frequent(2)
#


def is_subsequence(subseq, sequence):
    len_subseq = len(subseq)
    len_sequence = len(sequence)

    # If the subsequence is longer than the sequence, it cannot be a subsequence.
    if len_subseq > len_sequence:
        return False

    i, j = 0, 0

    # Iterate through both the subsequence and the sequence.
    while i < len_subseq and j < len_sequence:
        # Get the elements and strip if they are strings
        subseq_element = subseq[i].strip() if isinstance(subseq[i], str) else subseq[i]
        sequence_element = (
            sequence[j].strip() if isinstance(sequence[j], str) else sequence[j]
        )
        # If elements match, move to the next element in subsequence.
        if subseq_element == sequence_element:
            i += 1
        # Always move to the next element in sequence.
        j += 1

    # Check if all elements of subsequence were found in sequence.
    return i == len_subseq


print(
    is_subsequence(
        ["assignment_try_START", " assignment_sub_START"],
        [
            "assignment_vis_START",
            "forum_vis_START",
            "assignment_try_START",
            "assignment_sub_START",
        ],
    )
)

print(is_subsequence([1, 3], [1, 2, 3]))  # True
print(is_subsequence([1, 4], [1, 2, 3]))  # False
print(is_subsequence([], [1, 2, 3]))  # True
print(is_subsequence([1, 2, 3], [1, 2]))  # False
print(is_subsequence([2, 3], [1, 2, 3]))  # True

# # Combine sequences with their IDs
# results_with_ids = []
# for seq_tuple, support in results:
#     seq = seq_tuple  # seq_tuple is a tuple (sequence, support)
#     matching_ids = [id_ for id_, seq_data in data if is_subsequence(seq, seq_data)]
#     results_with_ids.append((seq, support, matching_ids))
#
# # Convert the results to a DataFrame
# df_results = pd.DataFrame(results_with_ids, columns=["Sequence", "Support", "IDs"])
#
# # Save the results to a CSV file
# # df_results.to_csv("prefixspan_results.csv", index=False)
#
# print(df_results)
