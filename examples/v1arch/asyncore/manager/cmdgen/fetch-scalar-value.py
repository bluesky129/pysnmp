"""Command Generator Application (GET)"""
from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
from pysnmp.carrier.asynsock.dgram.udp import UdpSocketTransport
from pysnmp.proto import omni
from time import time

# Protocol version to use
ver = omni.protoVersions[omni.protoVersionId1]

# Build message
req = ver.Message()
req.omniSetCommunity('public')

# Build PDU
req.omniSetPdu(ver.GetRequestPdu())
req.omniGetPdu().omniSetVarBindList(
    ((1,3,6,1,2,1,1,1,0), ver.Null()), ((1,3,6,1,2,1,1,2,0), ver.Null())
    )

def cbTimerFun(timeNow, startedAt=time()):
    if timeNow - startedAt > 3:
        raise "Request timed out"
    
def cbRecvFun(tspDsp, transportDomain, transportAddress, wholeMsg, req=req):
    rsp = ver.Message()
    while wholeMsg:
        wholeMsg = rsp.berDecode(wholeMsg)
        # Make sure this is a response to this request
        if req.omniMatch(rsp):
            errorStatus = rsp.omniGetPdu().omniGetErrorStatus()
            if errorStatus:
                print 'Error: ', errorStatus
            else:
                for varBind in rsp.omniGetPdu().omniGetVarBindList():
                    print varBind.omniGetOidVal()
    tspDsp.doDispatchFlag = 0
    return wholeMsg

dsp = AsynsockDispatcher(udp=UdpSocketTransport().openClientMode())
dsp.registerRecvCbFun(cbRecvFun)
dsp.registerTimerCbFun(cbTimerFun)
dsp.sendMessage(req.berEncode(), 'udp', ('localhost', 1161)) # 161
dsp.runDispatcher(liveForever=1)