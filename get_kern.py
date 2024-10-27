import os
from subprocess import check_call, check_output, call

# Create a file to store kernel versions
fp = open('raw_kern', 'w')
call(['ls', '/boot'], stdout=fp)

versions = []
with open('raw_kern', 'r') as fp:
    lines = fp.readlines()
    for l in lines:
        if 'vmlinuz' in l:
            full_name = l.strip('vmlinuz-').strip()
            # print full_name
            num_name = full_name.strip('-generic')
            if '-' in num_name:
                version_seg = num_name.split('-')
            elif 'c' in num_name:
                version_seg = num_name.split('c')
            elif 'd' in num_name:
                version_seg = num_name.split('d')

            first_versions = version_seg[0].split('.')
            ident = []
            print(version_seg)  # Added parentheses for compatibility with Python 3
            for s in first_versions:
                ident.append(int(s))
            length = len(ident)
            assert length == 3
            ident.append(full_name)
            versions.append(ident)

# Sort the versions
versions = sorted(versions, key=lambda x: (x[0], x[1], x[2]))

# Write the sorted kernel versions to a file
with open('kern_list', 'w') as fp:
    for v in versions:
        print(v)  # Added parentheses for compatibility with Python 3
        fp.write(v[3] + '\n')

# Remove the temporary file
os.remove('raw_kern')
