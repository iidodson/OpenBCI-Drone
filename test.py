import ps_drone
import time

drone = ps_drone.Drone()
drone.startup()
#
# print("Drone started...Would you like to take off y/n?")
#
# usr = raw_input("-> ")

# if(usr == 'y'):
drone.trim()
time.sleep(10)
drone.takeoff()
print "Dorne taking off"
time.sleep(1)
drone.hover()
print "Dorne is hovering"
time.sleep(30)
time.sleep(1)
drone.land()
print "Dorne is landing"
time.sleep(1)
print "Dorne has landed"
