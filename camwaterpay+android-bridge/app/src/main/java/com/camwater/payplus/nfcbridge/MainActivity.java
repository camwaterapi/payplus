package com.camwater.payplus.nfcbridge;

import android.app.Activity;
import android.content.Intent;
import android.nfc.NfcAdapter;
import android.nfc.Tag;
import android.nfc.tech.IsoDep;
import android.os.Bundle;
import android.widget.Toast;

public class MainActivity extends Activity implements NfcAdapter.ReaderCallback {
    private NfcAdapter adapter;
    private String tuiId;
    private String returnUrl;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Intent i = getIntent();
        if (i != null && i.getData() != null) {
            tuiId = i.getData().getQueryParameter("tid");
            returnUrl = i.getData().getQueryParameter("return");
        }
        adapter = NfcAdapter.getDefaultAdapter(this);
        if (adapter == null) {
            Toast.makeText(this, "NFC not supported", Toast.LENGTH_LONG).show();
            finish(); return;
        }
    }

    @Override protected void onResume() {
        super.onResume();
        if (adapter != null) {
            int flags = NfcAdapter.FLAG_READER_NFC_A | NfcAdapter.FLAG_READER_SKIP_NDEF_CHECK;
            adapter.enableReaderMode(this, this, flags, null);
            Toast.makeText(this, "Tap card to write", Toast.LENGTH_SHORT).show();
        }
    }
    @Override protected void onPause() { super.onPause(); if (adapter != null) adapter.disableReaderMode(this); }
    @Override public void onTagDiscovered(Tag tag) {
        try {
            IsoDep iso = IsoDep.get(tag);
            if (iso == null) { runOnUiThread(() -> Toast.makeText(this,"Not ISO-DEP",Toast.LENGTH_SHORT).show()); return; }
            iso.connect();
            // TODO: call backend /nfc/sessions/* (Retrofit) and exchange APDUs with iso.transceive(...)
            iso.close();
            if (returnUrl != null) { startActivity(new Intent(Intent.ACTION_VIEW, android.net.Uri.parse(returnUrl))); }
            finish();
        } catch (Exception e) { runOnUiThread(() -> Toast.makeText(this,"Error: "+e.getMessage(),Toast.LENGTH_LONG).show()); }
    }
}
