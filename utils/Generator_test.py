import sys

sys.path.insert(0, "..")

from new_shard_sim.ArchitectureGenerator import ArchitectureGenerator


root_shard, shard_array = ArchitectureGenerator.generate_architecture(
    number_shards=7, number_children=2, number_levels=3
)

print(f"root shard: {root_shard.id}")
print(f"root shard children: {root_shard.children}")

print(f"child 1 parent id {shard_array[1].parent.id}")
print(f"child 2 parent id {shard_array[2].parent.id}")
print(f"child 1 parent {shard_array[1].parent}")
print(f"child 2 parent {shard_array[2].parent}")

print(f"child 1 children {shard_array[1].children}")
print(f"child 2 children {shard_array[2].children}")

print(f"child 3 parent id {shard_array[3].parent.id}")
print(f"child 4 parent id {shard_array[4].parent.id}")

print(f"child 3 parent {shard_array[3].parent}")
print(f"child 4 parent {shard_array[4].parent}")
