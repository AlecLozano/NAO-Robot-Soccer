###
# Summary: this class will controll the use of all the sensors in the robot
# Parameters: 
# Return:
###

BALLEVENT = "31273"
SONAREVENT = "31274"
LANDMARKEVENT = "31275"
import time


class Sensor:
    def __init__(self, logger, config):
        ###
        # Summary: initialize Sensor class
        # Parameters: self, logger in which we will write all the important messages and config to
        #              activate all the configurations
        # Return:
        ###
        # asign the proxys to the variables
        self.logger = logger
        self.config = config
        self.touch = self.config.getProxy("ALTouch")
        self.tracker = self.config.getProxy("ALTracker")
        self.redBallDetection = self.config.getProxy("ALRedBallDetection")
        self.video = self.config.getProxy("ALVideoDevice")
        self.memory = self.config.getProxy("ALMemory")
        self.sonar = self.config.getProxy("ALSonar")
        self.sensors = self.config.getProxy("ALSensors")
        self.landmark = self.config.getProxy("ALLandMarkDetection")
        self.motion = self.config.getProxy("ALMotion")

        self.timeMillisOld = 0
        # write information into logger
        logger.info("Sensor-Class initialized")

    def getBallPosition(self):
        ###
        # Summary: give us the position of the ball
        # Parameters: self
        # Return: position of the ball
        ###
        return self.tracker.getTargetPosition()

    def getBallData(self):
        ###
        # Summary: this method will give us datas of the ball
        # Parameters: self
        # Return: data about the detected red ball
        ###
        return self.memory.getData("redBallDetected", 0)[1]
    
    

    def getTimeBallData(self):
        ###
        # Summary: this method will indicate if we have information in that moment about the
        #			ball
        # Parameters: self
        # Return: data in case we have information or 0 in case we don t have
        ###
        # load data from reBallDetected into data
        try:
            data = self.memory.getData("redBallDetected", 0)
            # if there is data
            if (data):
                # return data
                return data[0]
            else:
                # return 0
                return 0
        except:
            return 0
        
    def isHeadTouched(self):
        headStatus = self.touch.getStatus()[7:10]
        for sensor in headStatus:
            if sensor[1]:
                return True
        return False

    def getHeadAngle(self):
        ###
        # Summary: it will give us the angle of the head in that moment
        # Parameters: self
        # Return: angles of the head
        ###
        return self.motion.getAngles("HeadYaw", True)


    def isBallInHand(self):
        ###
        # Summary: This will indicate us if the ball is being grabbed by the hand
        # Parameters: self
        # Return: return if ball is in hand or not
        ###

        self.isIn = False

        # write information about right hand into logger
        self.logger.info("Hand Motor at: " + str(self.motion.getAngles("RHand", True)))
        # if angles of right hand are >= 0.5 then ball is in hand
        if (self.motion.getAngles("RHand", True) >= 0.5):
            self.isIn = True
        # write info into logger
        self.logger.info("Ball is in Hand: " + str(self.isIn))
        # return if ball is in hand or not
        return self.isIn

    def isNewBall(self):
        ###
        # Summary: indicate if Nao found the ball again after missing it
        # Parameters: self
        # Return: false if there is no data or it is old ball and true if it is new ball
        ###
        # get moment of last time Nao got data of the ball
        data = self.getTimeBallData()
        # if there is no data
        if (data == 0):
            return False

        # get moment of last time Nao got data of the ball
        timeMillis = self.getTimeBallData()[1]
        # write it on logger
        #self.logger.info("Time for last ball: " + str(timeMillis))

        # if data is not null
        if (data):
            return True
        else:
            return False

    def removeBallData(self):
        ###
        # Summary: delete data of the ball from memory
        # Parameters: self
        # Return: --
        ###
        # write info into logger
        self.logger.info("Deleting Memory Footprints")
        # remove data about redBallDetected from memory
        try:
            self.memory.removeData("redBallDetected")
        except:
            pass
        finally:
            self.logger.info("Ball data erased")

    # def startHeadTracker(self):
    #     ###
    #     # Summary: start head tracking of the ball
    #     # Parameters: self
    #     # Return: --
    #     ###
    #     # start tracking for the red ball

    #     self.tracker.registerTarget("RedBall", .06)
    #     #self.tracker.setMaximumDistanceDetection(2.0)
    #     self.tracker.setTimeOut(9000)

    #     X_axis_Distance = .01
    #     Y_axis_Distance = 0
    #     Theta = 0
    #     Thresh_X = .1255
    #     Thresh_Y = .2
    #     Thresh_theta = .3

    #     self.tracker.setRelativePosition([X_axis_Distance, Y_axis_Distance, Theta, Thresh_X, Thresh_Y, Thresh_theta])

    #     self.logger.info("Starting Tracker")
    #     self.tracker.setMode("Move")

        
    #     while True:
    #         self.tracker.track("RedBall")
    #         self.logger.info(str(self.tracker.isTargetLost()))

    #         if self.isHeadTouched():
    #             return "Head Touched"
            
    #     #self.logger.info(str(coord))
        
        # elif coord[0] > .008 and coord[2] > .123 and coord[3] > .28:
        #     #self.logger.info("Ball Reached :)")
        #     return "Target Reached"
        
        # elif self.isHeadTouched():
        #     return "Head Touched"
    def isTargetLost(self):
        self.tracker.isTargetLost()
        

    def stopHeadTracker(self):
        ###
        # Summary: stop head tracking of the ball
        # Parameters:
        # Return:
        ###
        # stop red ball tracking
        self.tracker.stopTracker()
        #self.removeBallData()

    def subscribeToRedball(self):
        ###
        # Summary: subscribe to the even (redBallDetection)
        # Parameters: self
        # Return: --
        ###
        # write into logger
        self.logger.info("Subscribing to Ball-Event")
        # subscribe to event BALLEVENT in redBallDetection
        self.redBallDetection.subscribe(BALLEVENT)

    def unsubscribeToRedBall(self):
        ###
        # Summary: unsubscribe from the eve (redBallDetection)
        # Parameters: self
        # Return: --
        ###
        self.logger.info("Unsubscribe from Ball-Event")
        # unsubscribe to event BALLEVENT in redBallDetection
        self.redBallDetection.unsubscribe(BALLEVENT)

    def setCamera(self, use):
        ###
        # Summary: change the parameters of the camera
        # Parameters: self, use determine which camera will be used. 0top 1bottom
        # Return: --
        ###
        # writting into logger
        self.logger.info("Trying to change Camera to: " + str(use))
        # use == 0, camera top
        if (use == 0):
            self.video.setParam(18, 0)
        # else, camera bottom
        elif (use == 1):
            self.video.setParam(18, 1)
        # else, wrong parameter for camera selection
        else:
            self.logger.warn("Wrong parameter for camera selection")

    def startSonar(self):
        ###
        # Summary: initialize the use of the sonar
        # Parameters: self
        # Return: --
        ###
        # write into logger
        self.logger.info("Subscribing to Sonar")
        # subscrive sonar to SONAREVENT. Start the sonar.
        self.sonar.subscribe(SONAREVENT, 500, 0.0)

    def stopSonar(self):
        ###
        # Summary: stop using the sonar
        # Parameters: self
        # Return: --
        ###
        # write into logger
        self.logger.info("Unsubscribe from Sonar")
        # unsubscribe the sonar to the event SONAREVET. Stop the sonar
        self.sonar.unsubscribe(SONAREVENT)

    def getSonarLeft(self):
        ###
        # Summary: get information from the left sonar
        # Parameters: self
        # Return: data with information from the left sonar
        ###
        # set information from the sonar into data
        data = self.memory.getData("Device/SubDeviceList/US/Left/Sensor/Value")
        # write the information from the sonar into logger
        self.logger.info(str(data))
        # return the value of data with the information of the sonar
        return data

    def getSonarRight(self):
        ###
        # Summary: get information from the right sonar
        # Parameters: self
        # Return: data with information from the right sonar
        ###
        # set information from the sonar into data
        data = self.memory.getData("Device/SubDeviceList/US/Right/Sensor/Value")
        # write the information from the sonar into logger
        self.logger.info(str(data))
        # return the value of data with the information of the sonar
        return data

    def subscribeToLandmarks(self):
        ###
        # Summary: subscribe to the event (landmark)
        # Parameters: self
        # Return: --
        ###
        # write into logger
        self.logger.info("Subscribing to Landmarks")
        # subscribe landmark into the event LANDMARKEVENT. Start recognition
        self.landmark.subscribe(LANDMARKEVENT, 200, 0.0)

    def unSubscribeFromLandMarks(self):
        ###
        # Summary: unsubscribe to the event (landmarkevent)
        # Parameters: self
        # Return: --
        ###
        # write into logger
        self.logger.info("Unsubscribing from Landmarks")
        # unsubscribe landmark from LANDMARKEVENT
        self.landmark.unsubscribe(LANDMARKEVENT)

    def getLandmarkAngle(self):
        ###
        # Summary: get the angle of the land mark
        # Parameters: self
        # Return: angle in case there is information inside the LandMark or 10 in contrary case
        ###
        # get position of landmark
        data = self.getLandmarkPosition()
        # if there is information in data
        if (data):
            # get the angle from the data
            angle = data[1][0][0][1]
            # write the angle into logger
            self.logger.info("Angle: " + str(angle))
            return angle
        else:
            return 10

    def getLandmarkDistance(self):
        ###
        # Summary: get the distance from Nao to the land mark
        # Parameters: self
        # Return: the distance till the landmark
        ###
        # get the information of the landmark position
        data = self.getLandmarkPosition()
        # if there is position
        if (data):
            # get information about the size
            sizeX = data[1][0][0][3]
            sizeY = data[1][0][0][4]
            self.size = 0
            if (sizeX >= sizeY):
                self.size = sizeX
            else:
                self.size = sizeY
            # check the distance from Nao till the landmark
            if (self.size <= 0.0622*4):
                return 1.5
            elif (self.size <= 0.0663*4):
                return 1.4
            elif (self.size <= 0.069*4):
                return 1.3
            elif (self.size <= 0.076*4):
                return 1.2
            elif (self.size <= 0.08*4):
                return 1.1
            elif (self.size <= 0.09*4):
                return 1
            elif (self.size <= 0.096*4):
                return 0.9
            elif (self.size <= 0.109*4):
                return 0.8
            elif (self.size <= 0.1228*4):
                return 0.7
            elif (self.size <= 0.1394*4):
                return 0.6
            elif (self.size <= 0.1626*4):
                return 0.5
            elif (self.size <= 0.2*4):
                return 0.4
            elif (self.size <= 0.2589*4):
                return 0.3
            elif (self.size <= 0.3685*4):
                return 0.2
            else:
                return 10

        else:
            return 10

    def getLandmarkPosition(self):
        ###
        # Summary: get the information from memory about land mark detected
        # Parameters: self
        # Return: data of landmark detected previously
        ###
        return self.memory.getData("LandmarkDetected")