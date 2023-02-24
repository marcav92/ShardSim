import inflect

from new_shard_sim.Shard import Shard
from new_shard_sim.Constants import BLOCK_CREATION_INTERVAL


class ArchitectureGenerator:
    p = inflect.engine()

    @classmethod
    def generate_architecture(cls, number_shards, number_children, number_levels):
        shard_array = []
        root_shard = None
        base_block_creation_interval = BLOCK_CREATION_INTERVAL
        # if not cls._is_topology_possible(number_shards, number_children, number_children):
        #     raise Exception("Topology combination is not possible")
        last_level_shards = None
        for level in range(number_levels):

            if level == 0:
                root_shard = Shard(block_creation_interval=base_block_creation_interval, name="root")
                last_level_shards = [root_shard]
                shard_array.append(root_shard)

            else:
                current_level_shards = []
                for upper_shard in last_level_shards:
                    for i in range(number_children):
                        current_shard = Shard(
                            block_creation_interval=int(
                                (base_block_creation_interval / 2**level)
                                - int((base_block_creation_interval / 2**level) * 0.1)
                            ),
                            name=cls.p.number_to_words(i),
                        )
                        current_shard.define_parent(upper_shard)
                        current_level_shards.append(current_shard)
                        shard_array.append(current_shard)

                        if len(shard_array) >= number_shards:
                            return root_shard, shard_array
                last_level_shards = current_level_shards

        return root_shard, shard_array

    def _is_topology_possible(number_shards, number_children, number_levels):
        traversed_number_of_levels = 0
        potential_number_shards = 0
        while traversed_number_of_levels < number_levels:
            if traversed_number_of_levels == 0:
                potential_number_shards += 1
            else:
                potential_number_shards *= number_children

            traversed_number_of_levels += 1

            if potential_number_shards > number_shards:
                if traversed_number_of_levels == number_levels:
                    return True
                else:
                    return False

        return False
