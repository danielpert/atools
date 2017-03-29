import mbuild as mb

from mbuild.lib.moieties import Silane

import atools
from atools.lib.chains.alkane import Alkane


class Alkylsilane(mb.Compound):
    """A functionalized alkylsilane chain. """
    def __init__(self, chain_length, hbonding_group, n_groups, locations):
        super(Alkylsilane, self).__init__()

        hmodule = __import__('atools.lib.moieties.multiple_ports.'+hbonding_group)
        hclass_ = getattr(hmodule.lib.moieties.multiple_ports, hbonding_group.title())
        hgroup = hclass_()

        # Determine alkane segments
        if isinstance(locations, int):
            locations = [locations]

        first_length = locations[0]
        first_segment = Alkane(first_length, cap_front=False, cap_end=False)
        self.add(first_segment, 'bottom_chain')
        silane = Silane()
        self.add(silane, 'silane')
        mb.force_overlap(self['silane'], self['silane']['up'], 
                         self['bottom_chain']['down'])
        self.add(silane['down'], 'down', containment=False)
        current_segment = first_segment

        c_remove = 0
        if hbonding_group in ['amide', 'hemiacetal']:
            c_remove += 1

        for i, loc in enumerate(locations[1:]):
            hgroup_clone = mb.clone(hgroup)
            self.add(hgroup_clone, 'hgroup{}'.format(i+1))
            mb.force_overlap(self['hgroup{}'.format(i+1)], 
                             self['hgroup{}'.format(i+1)]['down'],
                             current_segment['up'])
            length = loc - locations[i] - 1 - c_remove
            segment = Alkane(length, cap_front=False, cap_end=False)
            self.add(segment, 'internal_chain{}'.format(i+1))
            current_segment = segment
            mb.force_overlap(self['internal_chain{}'.format(i+1)],
                             self['internal_chain{}'.format(i+1)]['down'],
                             self['hgroup{}'.format(i+1)]['up'])

        self.add(hgroup, 'hgroup')
        mb.force_overlap(self['hgroup'], 
                         self['hgroup']['down'],
                         current_segment['up'])

        last_length = chain_length - locations[-1] - 1 - c_remove
        last_segment = Alkane(last_length, cap_front=True, cap_end=False)
        self.add(last_segment, 'top_chain')
        mb.force_overlap(self['top_chain'], self['top_chain']['down'],
                         self['hgroup']['up'])

if __name__ == "__main__":
    chain = Alkylsilane(chain_length=18, hbonding_group='methylene',
                        n_groups=2, locations=[3,6,10])
    chain.save('chain-hbond.mol2', overwrite=True)
