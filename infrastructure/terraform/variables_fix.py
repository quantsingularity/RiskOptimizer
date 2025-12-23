import re

# Read the variables.tf file
with open("variables.tf", "r") as f:
    content = f.read()

# Fix eks_node_group_desired_size validation - remove cross-var references
content = re.sub(
    r'(variable "eks_node_group_desired_size" \{[^}]+validation \{[^}]+condition = )\([^)]+\)',
    r"\1var.eks_node_group_desired_size >= 1",
    content,
    flags=re.DOTALL,
)

# Fix db_max_allocated_storage validation
content = re.sub(
    r'(variable "db_max_allocated_storage" \{[^}]+validation \{[^}]+condition[^=]+=\s+)var\.db_max_allocated_storage >= var\.db_allocated_storage',
    r"\1var.db_max_allocated_storage >= 20",
    content,
)

# Update error messages to be more generic
content = content.replace(
    "Desired node group size must be between minimum and maximum sizes.",
    "Desired node group size must be at least 1.",
)

content = content.replace(
    "Maximum allocated storage must be greater than or equal to initial allocated storage.",
    "Maximum allocated storage must be at least 20 GB.",
)

# Write back
with open("variables.tf", "w") as f:
    f.write(content)

print("✅ Fixed cross-variable validations in variables.tf")
