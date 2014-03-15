from BeeForm import BeeForm

form = BeeForm()
form.selectedbeeclass = form.beeclasses[1]
form.beearguments = form.selectedbeeclass.arguments()
form.checkbeearguments()
form.preparetheworld()
form.world.stepForward()
states = []
states.append(form.world.getworldState())
positions, bees, movement, communication = map(list, zip(*states[0]))
ownPos = positions[7]
otherPos = positions[:7] + positions[8:]
otherCom = communication[:7] + communication[8:]
trans = bees[7].transformation
form.world._accesableShortRangeCommunication(ownPos, otherPos, otherCom, trans)
