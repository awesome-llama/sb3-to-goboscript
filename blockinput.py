


class BlockInput():

    def __init__(self, block_slot=None, shadow_slot=None):
        
        # first slot, only expected to contain a block or null (though scratch technically allows other primitives to be placed here)
        if not (block_slot is None or isinstance(block_slot, (list, str))): 
            raise Exception('block slot is invalid')
        self.block_slot = block_slot 

        # second slot, contains shadow (which may be another block with shadow=true or more commonly a primitive value)
        if not (shadow_slot is None or isinstance(shadow_slot, (list, str))): 
            raise Exception('block slot is invalid')
        self.shadow_slot = shadow_slot 

    
    def to_list(self):
        """Convert to list format such as `[3, "a", [4, ""]]`"""
        
        # "1 = unobscured shadow, 2 = no shadow, 3 = obscured shadow"
        
        if self.shadow_slot is None:
            return [2, self.block_slot]
        
        if self.block_slot is None:
            return [1, self.shadow_slot]
        
        return [3, self.block_slot, self.shadow_slot]


    
    def __str__(self):
        return f"BlockInput({self.block_slot}, {self.shadow_slot})"


    def has_inserted_block(self):
        """True if a manually inserted (non-shadow) block exists"""
        return isinstance(self.block_slot, str)
    
    def has_shadow_block(self):
        """True if a shadow block exists (is referenced to by id)."""
        return isinstance(self.shadow_slot, str)
    
    def is_completely_empty(self):
        """True if the input has no block at all (not even shadow block), such as an empty boolean input or empty stack input"""
        return self.block_slot is None and self.shadow_slot is None


    def get_visible_slot_value(self):
        """Get a sensible readable value from the input."""

        if self.block_slot is not None:
            return BlockInput.get_slot_value(self.block_slot)
        return BlockInput.get_slot_value(self.shadow_slot)


    @classmethod
    def get_slot_value(cls, slot_contents):
        """Get a readable value from a slot."""
        if slot_contents is None:
            return None
        if isinstance(slot_contents, str):
            return slot_contents
        
        if 3 < slot_contents[0] < 11:
            return slot_contents[1]
        if slot_contents[0] == 11:
            return slot_contents[1] # slot_contents[2]
        if slot_contents[0] == 12 or slot_contents[0] == 13:
            return slot_contents[1]


    @classmethod
    def from_list(cls, data):
        """Constructor using Scratch JSON input format such as `[3, "a", [4, ""]]`."""
        
        self = cls() # create new object

        if data is None: return self # no data (such as a fallback when no input is found), use default.
        
        if data[0] == 1:
            self.shadow_slot = data[1]
        elif data[0] == 2:
            self.block_slot = data[1]
        elif data[0] == 3:
            self.block_slot = data[1]
            self.shadow_slot = data[2]
        
        else: raise Exception(f'unknown enum: {data[0]}')

        return self


if __name__ == '__main__':
    print(BlockInput().to_list())

    print(BlockInput('abc').to_list())

    print(BlockInput([11, 'broadcast name', 'g2hlrsz54fls']).to_list())

    print(BlockInput('def', 'ghi').to_list())

    print(BlockInput(None, [10, ""]).to_list())
    
    print(BlockInput('jkl', [10, ""]).to_list())

    print(BlockInput([10, ""], [10, ""]).to_list())

    print(BlockInput.from_list([1, 'block_id']))
    print(BlockInput.from_list([1, [10, 'text']]))
    print(BlockInput.from_list([2, 'block_id']))
    print(BlockInput.from_list([2, None]))
    print(BlockInput.from_list([3, 'block_id', [10, 'text']]))
    print(BlockInput.from_list([3, 'block_id1', 'block_id2']))