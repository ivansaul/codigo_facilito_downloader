const fs = require('fs');
const path = require('path');

const directorio = './'; // Reemplaza esto con la ruta de tu directorio

// Leer el contenido del directorio
fs.readdir(directorio, (error, archivos) => {
  if (error) {
    console.error('Error al leer el directorio:', error);
    return;
  }

  // Filtrar los archivos con extensión .zip
  const archivosZip = archivos.filter(archivo => path.extname(archivo) === '.rar');

  if (archivosZip.length === 0) {
    console.log('No se encontraron archivos .zip en el directorio.');
    return;
  }

  // Obtener el archivo más reciente
  const archivoMasReciente = archivosZip.reduce((archivo1, archivo2) => {
    const rutaArchivo1 = path.join(directorio, archivo1);
    const rutaArchivo2 = path.join(directorio, archivo2);
    const statsArchivo1 = fs.statSync(rutaArchivo1);
    const statsArchivo2 = fs.statSync(rutaArchivo2);
    return statsArchivo1.mtimeMs > statsArchivo2.mtimeMs ? archivo1 : archivo2;
  });

  const rutaArchivoMasReciente = path.join(directorio, archivoMasReciente);
  console.log('Ruta del archivo más reciente:', rutaArchivoMasReciente);
});


const { SmashUploader } = require('@smash-sdk/uploader');
const su = new SmashUploader({ region: "eu-west-3", token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjlhYjYyNjcyLWY1M2UtNGZlYy04Y2JjLTY3NGRmNDUzNDM5Yy1ldSIsInVzZXJuYW1lIjoiNzgzNGEzZDctMjdlMy00MGQyLTkzOGUtOTM5NDdlMTQ1Y2JhIiwicmVnaW9uIjoidXMtZWFzdC0xIiwiaXAiOiIxMDQuMjE3LjI0OC4yMiIsImFjY291bnQiOiJlMDcwMWM0OC03ZGIxLTQ3OGUtYWQ2OS1jMDIyOTZhOGI0ZWUtZWEiLCJpYXQiOjE2ODU1ODY2OTYsImV4cCI6NDg0MTM0NjY5Nn0.HQ9y4igkNygc2EtoXtXl_pZGN995_ILIu9vn80nFP1Y" })
const files = [
    rutaArchivoMasReciente,
];
su.upload({ files }).then(transfer => {
    console.log(transfer);
}).catch(error => {
    console.log(error);
});