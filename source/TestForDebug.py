from BeeForm import BeeForm

form = BeeForm()
form.selectedbeeclass = form.beeclasses[1]
form.beearguments = form.selectedbeeclass.arguments()
form.checkbeearguments()
form.preparetheworld()
states = []
states.append(form.world.getworldState())
positions, bees, movement, communication = map(list, zip(*states[0]))
