package com.embeddedsystems.camera.cameracontrol;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothSocket;
import android.content.Intent;
import android.os.Handler;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.Set;
import java.util.UUID;

public class ControlPanel extends AppCompatActivity {

    BluetoothSocket mmSocket;
    BluetoothDevice mmDevice = null;

    final byte delimiter = 33;
    int readBufferPosition = 0;


    public void sendBtMsg(String msg2send) {
        UUID uuid = UUID.fromString("94f39d29-7d6d-437d-973b-fba39e49d4ee"); //Standard SerialPortService ID
        try {
            mmSocket = mmDevice.createRfcommSocketToServiceRecord(uuid);
            if (!mmSocket.isConnected()) {
                mmSocket.connect();
            }

            OutputStream mmOutputStream = mmSocket.getOutputStream();
            mmOutputStream.write(msg2send.getBytes());

        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_control_panel);

        final Handler handler = new Handler();

        final TextView responseLabel = (TextView) findViewById(R.id.responseText);
        final Button switchModeButton = (Button) findViewById(R.id.switchModeButton);
        final Button captureButton = (Button) findViewById(R.id.captureButton);
        final Button turnOffButton = (Button) findViewById(R.id.turnOffButton);
        final Button enableSwitchesButton = (Button) findViewById(R.id.tactSwitches);

        BluetoothAdapter mBluetoothAdapter = BluetoothAdapter.getDefaultAdapter();

        final class workerThread implements Runnable {

            private String btMsg;

            public workerThread(String msg) {
                btMsg = msg;
            }

            public void run() {
                sendBtMsg(btMsg);
                while(!Thread.currentThread().isInterrupted()) {
                    int bytesAvailable;
                    boolean workDone = false;

                    try {
                        final InputStream mmInputStream;
                        mmInputStream = mmSocket.getInputStream();
                        bytesAvailable = mmInputStream.available();

                        if(bytesAvailable > 0) {

                            byte[] packetBytes = new byte[bytesAvailable];
                            Log.e("Raspi recv bt","bytes available");
                            byte[] readBuffer = new byte[1024];
                            mmInputStream.read(packetBytes);

                            for(int i=0;i<bytesAvailable;i++) {
                                byte b = packetBytes[i];
                                if(b == delimiter) {
                                    byte[] encodedBytes = new byte[readBufferPosition];
                                    System.arraycopy(readBuffer, 0, encodedBytes, 0, encodedBytes.length);
                                    final String data = new String(encodedBytes, "US-ASCII");
                                    readBufferPosition = 0;

                                    //The variable data now contains our full command
                                    handler.post(new Runnable() {
                                        public void run() {
                                            responseLabel.setText(data);
                                        }
                                    });

                                    workDone = true;
                                    break;
                                }
                                else {
                                    readBuffer[readBufferPosition++] = b;
                                }
                            }

                            if (workDone){
                                mmSocket.close();
                                break;
                            }
                        }
                    } catch (IOException e) {
                        e.printStackTrace();
                    }
                }
            }
        }

        /**
         * ActionListener: sends information to Raspberry due to switch between modes
          */
        switchModeButton.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                (new Thread(new workerThread("switch"))).start();

            }
        });

        /**
         * ActionListener: sends information to Raspberry due to capture a photo/video
         */
        captureButton.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                (new Thread(new workerThread("capture"))).start();

            }
        });

        /**
         * ActionListener: sends information to Raspberry due to turn off the program
         */
        turnOffButton.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                (new Thread(new workerThread("turnOff"))).start();
            }
        });

        /**
         * ActionListener: sends information to Raspberry due to enable tact switches
         */
        enableSwitchesButton.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                (new Thread(new workerThread("enaSwitches"))).start();
            }
        });

        if(!mBluetoothAdapter.isEnabled()) {
            Intent enableBluetooth = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
            startActivityForResult(enableBluetooth, 0);
        }

        Set<BluetoothDevice> pairedDevices = mBluetoothAdapter.getBondedDevices();
        if(pairedDevices.size() > 0) {
            for(BluetoothDevice device : pairedDevices) {
                if(device.getName().equals("raspberrypi")) { //Note, you will need to change this to match the name of your device
                    Log.e("Camera",device.getName());
                    mmDevice = device;
                    break;
                }
            }
        }
    }
}