# Original character string
original_string = "mfn535424500"
# Find the index of the first digit
index_of_first_digit = next((index for index, char in enumerate(original_string) if char.isdigit()), None)
# Split the string into two parts based on the index of the first digit
prefix = original_string[:index_of_first_digit]
suffix = original_string[index_of_first_digit:]
all = f'{prefix}{int(suffix)+1}'
print(all)
