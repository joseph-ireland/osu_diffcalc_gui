from PySide2 import QtCore, QtGui, QtWidgets
from collections import namedtuple
from PySide2.QtWidgets import QGraphicsItem


PLAY_AREA_WIDTH=512
PLAY_AREA_HEIGHT=384

OsuPoint = namedtuple("OsuPoint",("x","y","t"))

def radius(cs):
    return (512 / 16) * (1 - 0.7 * (cs - 5) / 5)

    

class PosCircle(QtWidgets.QGraphicsEllipseItem):
    def __init__(self, x, y, cs, editor):
        self.r = radius(cs)
        super().__init__(0,0,2*self.r,2*self.r)

        self.editor=editor

        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setPos(x-self.r,y-self.r)

    def setCs(self, cs):
        r = radius(cs)
        self.setWidth(2*self.r)
        self.setHeight(2*self.r)

    def itemChange(self, change, value):
        if (change == QtWidgets.QGraphicsItem.ItemPositionChange):
            newPos = value
            x = newPos.x()
            y = newPos.y()
            max_x = PLAY_AREA_WIDTH-2*self.r
            max_y = PLAY_AREA_HEIGHT-2*self.r
            if not 0 <= x <= max_x:
                newPos.setX(max(0, min(max_x, x)))
            if not 0 <= y <= max_y:
                newPos.setY(max(0, min(max_y,y)))
            
            self.editor.mapChanged.emit()
            return newPos
        
        return super().itemChange(change, value)
    

class TimeCircle(QtWidgets.QGraphicsEllipseItem):

    def __init__(self, diameter, editor):
        super().__init__(0,0,diameter,diameter)
        self.editor=editor
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)
    def itemChange(self, change, value):
        if (change == QtWidgets.QGraphicsItem.ItemPositionChange):
            newPos = value
            newPos.setY(0)
            precision = self.editor.snap_divisor
            newPos.setX(round(newPos.x() * precision) / precision)
            self.editor.mapChanged.emit()
            self.editor.updateIndexesTimer.start()

            return newPos
                
        return super().itemChange(change, value)


class EditorCircle:
    def __init__(self, index, cs, x, y, time, editor):
        self.pos_circle = PosCircle(x,y,cs, editor)
        self.pos_circle_label = QtWidgets.QGraphicsSimpleTextItem(self.pos_circle)
        #self.pos_circle_label.setFlag(QGraphicsItem.)
        self.time_circle = TimeCircle(44, editor)
        self.time_circle_label = QtWidgets.QGraphicsSimpleTextItem(self.time_circle)
        self.time_circle_label.setPos(20,15)
        self.time_circle.setPos(time,0)
        self.set_cs(cs)
        self.editor=editor
        self.index=None
        self.set_index(index)
        editor.window.addItem(self.pos_circle)
        
        editor.timeline.addItem(self.time_circle)
        self.editor.mapChanged.emit()




    @property
    def time(self):
        return self.time_circle.pos().x()

    def set_index(self, index):
        if index != self.index:
            self.index = index
            self.pos_circle_label.setText(str(index+1))
            self.time_circle_label.setText(str(index+1))

            #self.pos_circle.setZValue(-index)
            #self.time_circle.setZValue(-index)

    def set_cs(self, cs):
        r = radius(cs)
        rect = self.pos_circle.rect()
        rect.setWidth(2*r)
        rect.setHeight(2*r)
        self.pos_circle_label.setPos(r-3,r-7)
        self.pos_circle.setRect(rect)

    def remove(self):
        self.editor.window.removeItem(self.pos_circle)
        self.editor.timeline.removeItem(self.time_circle)
        self.editor.mapChanged.emit()
        self.editor.updateIndexesTimer.start()

class CircleGraphicsView(QtWidgets.QGraphicsView):
    deletePressed = QtCore.Signal()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)

    def keyPressEvent(self, event):
        if (event.key() in (QtGui.Qt.Key_Backspace, QtGui.Qt.Key_Delete)):
            self.deletePressed.emit()

        super().keyPressEvent(event)

class CircleGraphicsScene(QtWidgets.QGraphicsScene):
    sceneRightClicked = QtCore.Signal(QtCore.QPointF)

    def mousePressEvent(self, event):
        if event.button() == QtGui.Qt.MouseButton.RightButton:
            self.sceneRightClicked.emit(event.buttonDownScenePos(event.button()))

        super().mousePressEvent(event)


class CircleEditor(QtWidgets.QWidget):
    mapChanged = QtCore.Signal()

    def __init__(self,parent=None):
        super().__init__(parent)
        graphicsLayout = QtWidgets.QVBoxLayout()
        graphicsLayout.setMargin(0)
        self.setLayout(graphicsLayout)
        self.window=CircleGraphicsScene(self)
        self.windowView = CircleGraphicsView(self.window, self)
        self.window.setSceneRect(-10,-10,PLAY_AREA_WIDTH+20,PLAY_AREA_HEIGHT+20)
        self.windowView.deletePressed.connect(self.delete_selected)
        self.window.sceneRightClicked.connect(self.add_circle_at_qpoint)
        self.timeline=QtWidgets.QGraphicsScene(self)
        self.timeline.setSceneRect(0,0,1000,1)
        self.timelineView = CircleGraphicsView(self.timeline, self)
        self.timelineView.setMaximumHeight(50)
        self.window.selectionChanged.connect(self.update_selection)
        self.windowView.deletePressed.connect(self.delete_selected)


        graphicsLayout.addWidget(self.timelineView)
        graphicsLayout.addWidget(self.windowView)
        graphicsLayout.setStretch(1,1)


        self.circles=[]
        self.grid_lines=[]
        self.cs = 6
        self.snap_divisor=4
        self.updateIndexesTimer=QtCore.QTimer(self)
        self.updateIndexesTimer.setInterval(1)
        self.updateIndexesTimer.setSingleShot(True)
        self.updateIndexesTimer.timeout.connect(self.update_indexes)
    def update_indexes(self):
        self.circles = sorted(self.circles, key=lambda c: c.time)
        for i, circle in enumerate(self.circles):
            circle.set_index(i)

    def update_selection(self):
        items = set(self.window.selectedItems())
        time_circles = [circle.time_circle for circle in self.circles if circle.pos_circle in items]
        self.timeline.clearSelection()
        
        for circle in time_circles:
            circle.setSelected(True)

    def set_cs(self,cs):
        self.cs=cs
        for circle in self.circles:
            circle.set_cs(cs)

    def set_length(self, l):
        self.timeline.setSceneRect(0,0,l,1)
        self.timelineView.fitInView(self.timeline.sceneRect())

        if len(self.grid_lines) < l:
            for i in range(len(self.grid_lines), l):
                line = self.timeline.addLine(i,0,i,1, QtGui.QPen(QtGui.Qt.black,0))
                self.grid_lines.append(line)
        elif len(self.grid_lines)>l:
            for line in self.grid_lines[l:]:
                self.timeline.removeItem(line)
            
            del self.grid_lines[l:]



    def showEvent(self,event):
        self.windowView.fitInView(self.window.sceneRect(), QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        self.timelineView.fitInView(self.timeline.sceneRect())
        super().showEvent(event)


    def resizeEvent(self, event):
        self.windowView.fitInView(self.window.sceneRect(), QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        self.timelineView.fitInView(self.timeline.sceneRect())
        super().resizeEvent(event)

    def add_circle_at_point(self, x, y):
        self.timeline.clearSelection()
        self.timeline.clearFocus()
        time = self.circles[-1].time+1/self.snap_divisor if self.circles else 0

        newCircle = EditorCircle(len(self.circles), self.cs, x, y, time, self)
        self.circles.append(newCircle)

    def add_circle(self):
        self.add_circle_at_point(0,0)

    def add_circle_at_qpoint(self, point):
        self.add_circle_at_point(point.x(), point.y())

    def delete_selected(self):
        items = set(self.timeline.selectedItems())
        circles = [circle for circle in self.circles if circle.time_circle in items]
        for circle in circles:
            self.circles.remove(circle)
            circle.remove()

        for i, circle in enumerate(self.circles):
            circle.set_index(i)

    def get_points(self, bpm, length=0, repeats=1):
        return [OsuPoint(
            x=circle.pos_circle.pos().x(), 
            y=circle.pos_circle.pos().y(), 
            t=(j*length + circle.time_circle.pos().x()) * 60 * 1000/bpm
            ) for j in range(repeats) for circle in self.circles]        

    def add_slider_tick(self, index):
        pass

    def set_beat_divisor(self, i):
        self.snap_divisor = i

