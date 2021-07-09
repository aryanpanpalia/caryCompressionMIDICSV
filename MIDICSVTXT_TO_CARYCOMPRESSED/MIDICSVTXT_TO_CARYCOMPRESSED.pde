import java.io.InputStreamReader;

String fileFolder = "../1_midicsvtxt_files/";
String OUTPUT_FOLDER = "../2_carycompressed_files/";


int pitchCount = 110;
int[][] notes = new int[150000][pitchCount];
String[] filenames;
int currentInstrument = -1;
int firstTrackWithNotes = -1;
float quantizationSize = 40;
int minimumPitch = 22;
Boolean[] allow = new Boolean[128];
Boolean banThisPieceOfMusic = false;
Boolean haveSetTempo = false;

void setup(){
  File[] files = listFiles(fileFolder);
  filenames = new String[files.length];
  for (int i = 0; i < files.length; i++) {
    File f = files[i];
    filenames[i] = f.getName();
  }
}

void draw(){
  for(int fileIndex = 0; fileIndex < filenames.length; fileIndex++){
      banThisPieceOfMusic = false;
      for(int i = 0; i < 128; i++){
        allow[i] = true;
      }
      println("Starting file "+fileIndex);
      haveSetTempo = false;
      currentInstrument = -1;
      firstTrackWithNotes = -1;
      String thisFile = filenames[fileIndex];
      
      println(fileFolder+thisFile);
      
      String[] data = loadStrings(fileFolder+thisFile);
      for(int i = 0; i < 150000; i++){
        for(int j = 0; j < pitchCount; j++){
          notes[i][j] = 0;
        }
      }
      int maxPitch = 0;
      int minPitch = 99999;
      int finalTime = 0;
      for(int i = 0; i < data.length; i++){
        String[] parts = data[i].split(", ");
        if(parts.length >= 3 && parts[2].equals("Tempo")){
          if(haveSetTempo){ // MIDI changed "tempo", making it confusing... BAN IT
            banThisPieceOfMusic = true;
          }else{
            float division = (float)(Integer.parseInt(data[0].split(", ")[5]));
            float tempo = (float)(Integer.parseInt(parts[3]));
            quantizationSize = (50000.0/tempo)*division; //40
            println(quantizationSize);
          }
        }
        if(parts.length >= 5){
          String s = parts[2];
          if(s.equals("Program_c")){
            currentInstrument = Integer.parseInt(parts[4]);
            allow[Integer.parseInt(parts[3])] = (currentInstrument >= 0 && currentInstrument <= 7);
          }
        }
        if(parts.length >= 6 && data[i].indexOf("\"") == -1){
          int thisTrack = Integer.parseInt(parts[0]);
          if(allow[Integer.parseInt(parts[3])]){
            firstTrackWithNotes = thisTrack;
            String s = parts[2];
            int time = (int)((Integer.parseInt(parts[1])/quantizationSize));
            int inst = Integer.parseInt(parts[0]);
            int pitch = Integer.parseInt(parts[4]);
            int volume = Integer.parseInt(parts[5]);
            if(time < 150000 && inst <= 8){
              if(s.equals("Note_on_c") && volume >= 1 && notes[time][pitch] == 0){ // File 988 requires volume of 100, not 127.
                notes[time][pitch] = 1;
                if(pitch > maxPitch){
                  maxPitch = pitch;
                }
                if(pitch < minPitch){
                  minPitch = pitch;
                }
                if(time >= finalTime){
                  finalTime = time;
                }
              }else if((s.equals("Note_on_c") && volume == 0) || s.equals("Note_off_c")){
                int j = time;
                while(j >= 0 && notes[j][pitch]%2 == 0){
                  j--;
                }
                if(j >= 0){
                  int end = time-1;
                  if(end < j+1){
                    end = j+1;
                  }
                  for(int k = j; k < end; k++){
                    notes[k][pitch] = floor(notes[k][pitch]/2)*2+2;
                  }
                  if(end-1 >= finalTime){
                    finalTime = end-1;
                  }
                }
              }
            }
          }
        }
      }
      if(banThisPieceOfMusic){
        println(thisFile+" WILL BE ABORTED");
      }else{
        boolean turnedOn = false;
        for(int transposition = 0; transposition < 6; transposition++){
          PrintWriter output = createWriter(OUTPUT_FOLDER+"/text"+fileIndex+"_"+transposition+".txt");
          for(int x = 0; x < min(150000,finalTime+24); x++){
            for(int y = 24; y < pitchCount; y++){
              if(notes[x][y] >= 1){
                int theNum = (33+(y-minimumPitch+transposition));
                if(theNum >= 33 && theNum <= 126){
                  output.print((char)(theNum));
                  turnedOn = true;
                }
              }
            }
            if(turnedOn){
              output.print(" ");
            }
            if(x%50 == 49){
              output.println("");
            }
          }
          output.flush();
          output.close();
        }
      }
    
      println(thisFile+" Done");
      if(fileIndex >= filenames.length-1){
        exit();
      }
    }
}
