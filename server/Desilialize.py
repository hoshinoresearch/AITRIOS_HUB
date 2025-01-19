
import base64
import flatbuffers


class ObjectDetectionTop(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAs(cls, buf, offset=0):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = ObjectDetectionTop()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def GetRootAsObjectDetectionTop(cls, buf, offset=0):
        """This method is deprecated. Please switch to GetRootAs."""
        return cls.GetRootAs(buf, offset)
    # ObjectDetectionTop
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # ObjectDetectionTop
    def Perception(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            x = self._tab.Indirect(o + self._tab.Pos)
            obj = ObjectDetectionData()
            obj.Init(self._tab.Bytes, x)
            return obj
        return None

class ObjectDetectionData(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAs(cls, buf, offset=0):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = ObjectDetectionData()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def GetRootAsObjectDetectionData(cls, buf, offset=0):
        """This method is deprecated. Please switch to GetRootAs."""
        return cls.GetRootAs(buf, offset)
    # ObjectDetectionData
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # ObjectDetectionData
    def ObjectDetectionList(self, j):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            x = self._tab.Vector(o)
            x += flatbuffers.number_types.UOffsetTFlags.py_type(j) * 4
            x = self._tab.Indirect(x)
            obj = GeneralObject()
            obj.Init(self._tab.Bytes, x)
            return obj
        return None

    # ObjectDetectionData
    def ObjectDetectionListLength(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

    # ObjectDetectionData
    def ObjectDetectionListIsNone(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        return o == 0
    
class GeneralObject(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAs(cls, buf, offset=0):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = GeneralObject()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def GetRootAsGeneralObject(cls, buf, offset=0):
        """This method is deprecated. Please switch to GetRootAs."""
        return cls.GetRootAs(buf, offset)
    # GeneralObject
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # GeneralObject
    def ClassId(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Uint32Flags, o + self._tab.Pos)
        return 0

    # GeneralObject
    def BoundingBoxType(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Uint8Flags, o + self._tab.Pos)
        return 0

    # GeneralObject
    def BoundingBox(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
        if o != 0:
            from flatbuffers.table import Table
            obj = Table(bytearray(), 0)
            self._tab.Union(obj, o)
            return obj
        return None

    # GeneralObject
    def Score(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Float32Flags, o + self._tab.Pos)
        return 0.0
    
class BoundingBox(object):
    NONE = 0
    BoundingBox2d = 1

class BoundingBox2d(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAs(cls, buf, offset=0):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = BoundingBox2d()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def GetRootAsBoundingBox2d(cls, buf, offset=0):
        """This method is deprecated. Please switch to GetRootAs."""
        return cls.GetRootAs(buf, offset)
    # BoundingBox2d
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # BoundingBox2d
    def Left(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Int32Flags, o + self._tab.Pos)
        return 0

    # BoundingBox2d
    def Top(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Int32Flags, o + self._tab.Pos)
        return 0

    # BoundingBox2d
    def Right(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Int32Flags, o + self._tab.Pos)
        return 0

    # BoundingBox2d
    def Bottom(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Int32Flags, o + self._tab.Pos)
        return 0

class DeserializeUtil:
    def get_deserialize_data(self, serialize_data):
        """Get access information from yaml and generate ConsoleAccess client
        Returns:
            ConsoleAccessClient: CosoleAccessClient Class generated from access information.
        """
        buf = {}
        buf_decode = base64.b64decode(serialize_data)
        ppl_out = ObjectDetectionTop.GetRootAsObjectDetectionTop(buf_decode, 0)
        obj_data = ppl_out.Perception()
        res_num = obj_data.ObjectDetectionListLength()
        for i in range(res_num):
            obj_list = obj_data.ObjectDetectionList(i)
            union_type = obj_list.BoundingBoxType()
            if union_type == BoundingBox.BoundingBox2d:
                bbox_2d = BoundingBox2d()
                bbox_2d.Init(obj_list.BoundingBox().Bytes, obj_list.BoundingBox().Pos)
                buf[str(i + 1)] = {}
                buf[str(i + 1)]['C'] = obj_list.ClassId()
                buf[str(i + 1)]['P'] = obj_list.Score()
                buf[str(i + 1)]['X'] = bbox_2d.Left()
                buf[str(i + 1)]['Y'] = bbox_2d.Top()
                buf[str(i + 1)]['x'] = bbox_2d.Right()
                buf[str(i + 1)]['y'] = bbox_2d.Bottom()

        return buf