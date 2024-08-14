package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"net/smtp"
	"strconv"
	"time"

	"github.com/jordan-wright/email"
	"github.com/xuri/excelize/v2"
	"gopkg.in/yaml.v2"
)

type Config struct {
	API struct {
		URL   string `yaml:"url"`
		Token string `yaml:"token"`
	} `yaml:"api"`
	QueriesBySource  map[string][]QueryConfig `yaml:"queries_by_source"`
	NamespacesTenant []string                 `yaml:"namespaces-tenants"`
	Email            struct {
		From     string `yaml:"from"`
		To       string `yaml:"to"`
		Subject  string `yaml:"subject"`
		SMTPHost string `yaml:"smtp_host"`
		SMTPPort string `yaml:"smtp_port"`
		Username string `yaml:"username"`
		Password string `yaml:"password"`
	} `yaml:"email"`
}

type QueryConfig struct {
	Metric    string `yaml:"metric"`
	Source    string `yaml:"source"`
	Timeframe string `yaml:"timeframe"`
	Label     string `yaml:"label"`
}

type QueryResponse struct {
	Status string `json:"status"`
	Data   struct {
		ResultType string `json:"resultType"`
		Result     []struct {
			Metric map[string]string `json:"metric"`
			Values [][]interface{}   `json:"values"`
		} `json:"result"`
	} `json:"data"`
}

var metricLabels = map[string]string{
	"container_cpu_usage_seconds_total":      "CPU SHARE",
	"kubelet_volume_stats_used_bytes":        "STORAGE SHARE",
	"container_memory_usage_bytes":           "MEMORY SHARE",
	"storage_size_bucket":                    "STORAGE SIZE S3",
	"container_network_transmit_bytes_total": "EGRESS SHARE",
	"s3_total_get_response_size_in_bytes":    "S3 GET SHARE",
	"s3_total_put_request_size_in_bytes":     "S3 PUT SHARE",
	"s3_total_head_response_size_in_bytes":   "S3 HEAD SHARE",
	"s3_total_number_of_put_requests":        "S3 Amount of PUT SHARE",
	"s3_total_number_of_get_requests":        "S3 Amount of GET Share",
	"s3_total_number_of_head_requests":       "S3 Amount of HEAD Share",
}

func makeQuery(config Config, query, startTime, endTime, step string) ([]byte, error) {
	req, err := http.NewRequest("GET", config.API.URL, nil)
	if err != nil {
		return nil, err
	}

	q := req.URL.Query()
	q.Add("query", query)
	q.Add("start", startTime)
	q.Add("end", endTime)
	q.Add("step", step)
	req.URL.RawQuery = q.Encode()

	req.Header.Add("Authorization", fmt.Sprintf("Bearer %s", config.API.Token))
	req.Header.Add("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		log.Printf("Failed to read response body: %s\n", err)
		return nil, err
	}

	fmt.Printf("Raw API response for query %s: %s\n", query, string(body)) // Log raw response

	return body, nil
}

func getPreviousMonthRange() (string, string) {
	now := time.Now()
	firstDayOfCurrentMonth := time.Date(now.Year(), now.Month(), 1, 0, 0, 0, 0, time.UTC)
	lastDayOfPreviousMonth := firstDayOfCurrentMonth.AddDate(0, 0, -1)
	firstDayOfPreviousMonth := time.Date(lastDayOfPreviousMonth.Year(), lastDayOfPreviousMonth.Month(), 1, 0, 0, 0, 0, time.UTC)

	start := firstDayOfPreviousMonth.Format(time.RFC3339)
	end := lastDayOfPreviousMonth.Format(time.RFC3339)
	return start, end

}

// generateQuery constructs Prometheus query strings for the specified metric, timeframe, source, and namespaces.
// It returns a slice of query strings.
// problem here with NAMESPACE label when we want to query by source
// because of config, had to make those metrics double for namespace and only source or
// just rewrite config... hmm
func generateQuery(metric, timeframe, source string, namespaces []string, label string) []string {
	var queries []string
	var query string

	switch label {
	case "tenant":
		for _, tenant := range namespaces {
			query = fmt.Sprintf(`sum(%s{tenant=~"%s", source=~"%s"}[%s])`, metric, tenant, source, timeframe)
			queries = append(queries, query)
		}
	case "namespace":
		for _, namespace := range namespaces {
			query = fmt.Sprintf(`sum(%s{namespace=~"%s", source=~"%s"}[%s])`, metric, namespace, source, timeframe)
			queries = append(queries, query)
		}
	case "source":
		query = fmt.Sprintf(`sum(%s{source=~"%s"}[%s])`, metric, source, timeframe)
		queries = append(queries, query)
	}
	fmt.Println("Generated Queries:", queries)
	return queries
}

// calculateTotalLastValue calculates the sum of the last values of each day for the given QueryResponse data.
// It returns the total sum as a float64.
func calculateTotalLastValue(data QueryResponse) float64 {
	dailyValues := make(map[string]float64)
	for _, result := range data.Data.Result {
		for _, value := range result.Values {
			timestampSec, _ := strconv.ParseFloat(fmt.Sprintf("%v", value[0]), 64)
			valueFloat, _ := strconv.ParseFloat(fmt.Sprintf("%v", value[1]), 64)
			date := time.Unix(int64(timestampSec), 0).UTC().Format("2006-01-02")
			if current, exists := dailyValues[date]; !exists || valueFloat > current {
				dailyValues[date] = valueFloat
			}
		}
	}
	var total float64
	for _, v := range dailyValues {
		total += v
	}
	return total
}

// calculateTotalAndQueryValues executes the queries within the specified timeframe and calculates the total and individual query values.
// It returns the total metric value and a slice of individual query metric values.

func calculateTotalAndQueryValues(config Config, queries []string, startTime, endTime, timeframe string) (float64, []float64) {
	var totalMetric float64
	var queryMetrics []float64

	for _, query := range queries {
		response, err := makeQuery(config, query, startTime, endTime, timeframe)
		if err != nil {
			log.Fatal(err)
		}

		var queryResponse QueryResponse
		if err := json.Unmarshal(response, &queryResponse); err != nil {
			log.Fatal(err)
		}
		fmt.Printf("Raw API response for query %s: %s\n", query, string(response))

		lastValue := calculateTotalLastValue(queryResponse)
		queryMetrics = append(queryMetrics, lastValue)
		totalMetric += lastValue
		fmt.Printf("Calculated last value for query %s: %f\n", query, lastValue)
	}

	return totalMetric, queryMetrics
}

// calculatePercentShares computes the percentage shares of each query metric relative to the total metric value.
// It returns a slice of percentage shares as float64.
func calculatePercentShares(totalMetric float64, queryMetrics []float64) []float64 {
	var percentShares []float64
	if totalMetric == 0 {
		for range queryMetrics {
			percentShares = append(percentShares, 0)
		}
	} else {
		for _, metric := range queryMetrics {
			percentShares = append(percentShares, (metric/totalMetric)*100)
		}
	}
	return percentShares
}

// loadConfig reads the configuration from a YAML file and unmarshals it into a Config struct.
// It returns the Config struct and an error if any occurred during file reading or unmarshalling.

func loadConfig(configFile string) (Config, error) {
	var config Config
	data, err := ioutil.ReadFile(configFile)
	if err != nil {
		return config, err
	}

	err = yaml.Unmarshal(data, &config)
	return config, err
}

// writeToExcel writes the provided data to an Excel file with the specified file path and sheet names.
// It logs a fatal error if any issue occurs during file creation or writing.

func writeToExcel(filePath string, sheets map[string][][]string) {
	f := excelize.NewFile()

	for sheetName, data := range sheets {
		index, err := f.NewSheet(sheetName)
		if err != nil {
			fmt.Println("Problem with creating new sheet", err)
		}

		for rowIndex, row := range data {
			for colIndex, cell := range row {
				axis, _ := excelize.CoordinatesToCellName(colIndex+1, rowIndex+1)
				if cell == "0" { // Check if the cell value is "0"
					f.SetCellValue(sheetName, axis, "") // Set an empty cell if the value is zero
				} else {
					f.SetCellValue(sheetName, axis, cell)
				}
			}
		}
		f.SetActiveSheet(index)
	}

	if err := f.SaveAs(filePath); err != nil {
		log.Fatal("Unable to save Excel file:", err)
	}

	fmt.Printf("Data written to Excel file: %s\n", filePath)
}

func sendEmailWithAttachment(config Config, filePath string) error {
	e := email.NewEmail()
	e.From = config.Email.From
	e.To = []string{config.Email.To}
	e.Subject = config.Email.Subject
	e.Text = []byte("Please find the attached Excel file.")
	_, err := e.AttachFile(filePath)
	if err != nil {
		return err
	}

	auth := smtp.PlainAuth("", config.Email.Username, config.Email.Password, config.Email.SMTPHost)
	return e.Send(config.Email.SMTPHost+":"+config.Email.SMTPPort, auth)
}

func main() {

	configFilePath := flag.String("config", "", "Path to configuration")
	flag.Parse()
	config, err := loadConfig(*configFilePath)
	if err != nil {
		log.Fatal("Failed to load config:", err)
	}

	startTime, endTime := getPreviousMonthRange()
	excelData := make(map[string][][]string)

	fmt.Println("Start Time:", startTime, "End Time:", endTime)

	for source, queries := range config.QueriesBySource {
		results := make(map[string]map[string]float64)

		for _, namespace := range config.NamespacesTenant {
			results[namespace] = make(map[string]float64)
		}

		headers := prepareHeaders(queries)
		var sheetData [][]string
		sheetData = append(sheetData, headers)

		for _, queryConfig := range queries {
			queryList := generateQuery(queryConfig.Metric, queryConfig.Timeframe, source, config.NamespacesTenant, queryConfig.Label)
			totalMetric, queryMetrics := calculateTotalAndQueryValues(config, queryList, startTime, endTime, queryConfig.Timeframe)

			fmt.Printf("Source: %s, Metric: %s, Total Metric: %f\n", source, queryConfig.Metric, totalMetric)
			percentShares := calculatePercentShares(totalMetric, queryMetrics)

			for i, namespace := range config.NamespacesTenant {
				if i < len(percentShares) {
					results[namespace][queryConfig.Metric] = percentShares[i]
				} else {
					results[namespace][queryConfig.Metric] = 0
				}
				fmt.Printf("Namespace: %s, Metric: %s, Share: %f\n", namespace, queryConfig.Metric, results[namespace][queryConfig.Metric])
			}
		}
		//only non zero values should be in excel
		for _, namespace := range config.NamespacesTenant {
			row := []string{namespace}
			isNonZero := false
			for _, queryConfig := range queries {
				value := fmt.Sprintf("%.2f", results[namespace][queryConfig.Metric])
				if value != "0.00" {
					isNonZero = true
				}
				row = append(row, value)
			}
			if isNonZero {
				sheetData = append(sheetData, row)
			}
		}
		excelData[source] = sheetData
	}

	fmt.Println("Start Time:", startTime, "End Time:", endTime)
	formattedStartTime := startTime[:10]
	formattedEndTime := endTime[:10]
	fileName := fmt.Sprintf("output_%s_to_%s.xlsx", formattedStartTime, formattedEndTime)

	writeToExcel(fileName, excelData)
	if err := sendEmailWithAttachment(config, fileName); err != nil {
		log.Fatal("Failed to send email:", err)
	}
}

func prepareHeaders(metrics []QueryConfig) []string {
	headers := []string{"Tenant/Namespace"}
	for _, metric := range metrics {
		label, exists := metricLabels[metric.Metric]
		if !exists {
			label = metric.Metric
		}
		header := fmt.Sprintf("%s Share (%%)", label)
		headers = append(headers, header)
	}
	return headers
}
