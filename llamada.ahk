f6::	
MsgBox, 52, Alerta, ¿Vols emitir una alerta?
IfMsgBox Yes 
{
	Run AlrtDB.py, C:\Users\david\Desktop
}
Return
