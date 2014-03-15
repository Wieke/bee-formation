from BeeForm import BeeForm

form = BeeForm()
form.selectedbeeclass = form.beeclasses[1]
form.beearguments = form.selectedbeeclass.arguments()
form.checkbeearguments()
form.preparetheworld()
