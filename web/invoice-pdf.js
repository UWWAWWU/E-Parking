// Vector text on a compact receipt page. Fonts are subset to the invoice content.
export async function createInvoicePdf(receipt,language,details,{PDFDocument,rgb,fontkit,fontBytes}){
  const doc=await PDFDocument.create();
  doc.registerFontkit(fontkit);
  const font=await doc.embedFont(fontBytes,{subset:true});
  const width=240,margin=16,gap=4,bodySize=9,lineHeight=13;
  const wrap=(value,maxWidth,size=bodySize)=>{
    const lines=[];let line='';
    for(const char of String(value)){
      if(char==='\n'){lines.push(line);line='';continue;}
      if(line&&font.widthOfTextAtSize(line+char,size)>maxWidth){lines.push(line.trimEnd());line=char===' '?'':char;}
      else line+=char;
    }
    lines.push(line);return lines;
  };
  const rows=details.map(([label,value])=>({label,value:wrap(value,width-margin*2),labelLines:wrap(label,width-margin*2,8)}));
  const note=language==='id'?'Bukti transaksi simulasi E-Parking.':'E-Parking simulated transaction receipt.';
  const footer=wrap(note,width-margin*2,8);
  const height=160+rows.reduce((sum,row)=>sum+row.labelLines.length*11+row.value.length*lineHeight+gap+8,0)+footer.length*11+margin;
  const page=doc.addPage([width,height]);
  const ink=rgb(.14,.15,.23),muted=rgb(.38,.4,.46),gold=rgb(.98,.77,0);
  const draw=(text,x,top,size=bodySize,color=ink)=>page.drawText(String(text),{x,y:height-top-size,size,font,color});
  const line=top=>page.drawLine({start:{x:margin,y:height-top},end:{x:width-margin,y:height-top},thickness:.6,color:rgb(.8,.81,.85)});
  page.drawRectangle({x:0,y:height-5,width,height:5,color:gold});
  draw('E-PARKING',margin,17,10);draw('Invoice',margin,34,22);
  draw(receipt.id,margin,64,8,muted);
  draw(language==='id'?'TRANSAKSI SELESAI':'PAYMENT COMPLETED',margin,83,8,rgb(.15,.46,.28));
  line(106);let top=118;
  for(const row of rows){for(const label of row.labelLines){draw(label,margin,top,8,muted);top+=11;}top+=gap;for(const value of row.value){draw(value,margin,top);top+=lineHeight;}top+=8;}
  line(top);top+=12;
  const total='Rp'+receipt.total.toLocaleString('id-ID');
  draw('Total',margin,top,12);draw(total,width-margin-font.widthOfTextAtSize(total,14),top,14);top+=30;
  for(const value of footer){draw(value,margin,top,8,muted);top+=11;}
  doc.setTitle(`E-Parking Invoice ${receipt.id}`);doc.setAuthor('E-Parking');doc.setSubject(note);
  return doc.save();
}
