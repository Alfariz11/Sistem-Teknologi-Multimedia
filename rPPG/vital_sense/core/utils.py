import time

class FPSCounter:
    """Calculates Frames Per Second."""
    def __init__(self, avg_frames=30):
        self.avg_frames = avg_frames
        self.frame_times = []

    def update(self):
        self.frame_times.append(time.time())
        if len(self.frame_times) > self.avg_frames:
            self.frame_times.pop(0)

    def get_fps(self):
        if len(self.frame_times) < 2:
            return 0.0
        diff = self.frame_times[-1] - self.frame_times[0]
        if diff == 0: return 0.0
        return (len(self.frame_times) - 1) / diff
