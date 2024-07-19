package com.example.my_sample_application.ui.dashboard

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import java.net.HttpURLConnection
import java.net.URL

class DashboardViewModel : ViewModel() {

    private val _text = MutableLiveData<String>()
    val text: LiveData<String> = _text

    init {
        fetchData()
    }

    private fun fetchData() {
        viewModelScope.launch(Dispatchers.IO) {
            try {
                val url = URL("https://chaos-monkey-ai.vercel.app/api/hello")
                val connection = url.openConnection() as HttpURLConnection
                connection.requestMethod = "GET"

                if (connection.responseCode == HttpURLConnection.HTTP_OK) {
                    val response = connection.inputStream.bufferedReader().use { it.readText() }
                    // Assuming the response is in JSON format and has a "message" field
                    val message = extractMessageFromJson(response)
                    _text.postValue(message)
                } else {
                    _text.postValue("Error: ${connection.responseCode}")
                }
            } catch (e: Exception) {
                _text.postValue("Error: ${e.message}")
            }
        }
    }

    private fun extractMessageFromJson(jsonString: String): String {
        // This is a simple way to extract the "message" field from JSON
        // For production code, consider using a proper JSON parsing library
        val messageRegex = """"message"\s*:\s*"([^"]+)"""".toRegex()
        val matchResult = messageRegex.find(jsonString)
        return matchResult?.groupValues?.get(1) ?: "Message not found in response"
    }
}