import simpy

def driver(env, car):
     yield env.timeout(5)
     print car.action
     if car.action != None:
         car.action.interrupt()
         print "b"
     
class Car(object):
     def __init__(self, env):
         self.env = env
         self.action = env.process(self.run())

     def run(self):
         while True:
             print('Start parking and charging at %d' % self.env.now)
             charge_duration = 3
             # We may get interrupted while charging the battery
             try:
                 yield self.env.process(self.charge(charge_duration))
             except simpy.Interrupt:
                 # When we received an interrupt, we stop charging and
                 # switch to the "driving" state
                 print('Was interrupted. Hope, the battery is full enough ...')

             print('Start driving at %d' % self.env.now)
             trip_duration = 3
             print "before timeout"
             try:
                yield self.env.timeout(trip_duration)
             except simpy.Interrupt:
                 # When we received an interrupt, we stop charging and
                 # switch to the "driving" state
                 print('Dang timeout bi interupt')
                 
             print "after timeout"

     def charge(self, duration):
         yield self.env.timeout(duration)

env = simpy.Environment()
car = Car(env)
env.process(driver(env, car))
env.run(until=15)