f6::	
MsgBox, 52, Alerta, ¿Vols emitir una alerta?
IfMsgBox Yes 
{
	Run test.py 192.168.1.12 80 1, C:\Users\david\Desktop
}
Return
