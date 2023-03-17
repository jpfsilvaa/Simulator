import threading

class PredictionsSingleton:
    _instance = None
    _lock = threading.Lock()
    predictions = dict()

    def __new__(cls):
        if cls._instance is None: 
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def storePredictionsAndResults(self, timeStep, predictionsList, realResults):
        self.predictions[timeStep] = (predictionsList, realResults)

    def getPredictionsAndResPairs(self):
        return self.predictions

    def getPredictions(self):
        return [t[0] for t in self.predictions.values()]

    def getRealResults(self):
        return [t[1] for t in self.predictions.values()]
    
    def getPredictionsAndResFromTimestep(self, timeStep):
        return self.predictions[timeStep]