# IP2Domain - Advanced Network Reconnaissance Tool

## Summary

IP2Domain is an advanced network reconnaissance tool designed for cybersecurity professionals, threat researchers, and system administrators. Its purpose is to enable deep and efficient analysis of large-scale networks, focusing on discovering web servers and analyzing IP addresses while always maintaining user privacy and security.

IP2Domain offers capabilities that stand out for their technical robustness, allowing massive scans of IP addresses, storing data in SQLite databases, and ensuring complete anonymity thanks to integration with the Tor network. It is a solution that combines speed, scalability, and anonymity, ideal for use in security tasks and network infrastructure assessments.

## Highlighted Qualities

- **Performance Optimization with Parallel Processes**: The implementation uses a concurrent approach to process multiple IP addresses simultaneously, maximizing system resource usage through the integration of parallel processes and threads. This ensures greater efficiency in large-scale operations.

- **Resilience Against Network Errors**: The use of the backoff library in combination with controlled exceptions to handle common network errors (such as redirects, SSL failures, and connection errors) ensures that the script can continue operating even under adverse conditions, improving its robustness and minimizing unexpected interruptions.

- **Adaptability with Different Data Sources**: The tool allows for working with both a single CIDR file and directories containing multiple files, offering greater flexibility in processing different datasets in dynamic environments.

- **Complete Interaction with Tor**: Native integration with the Tor network through the use of SOCKS5 proxies ensures that all connections are made securely and anonymously, allowing for the analysis of hidden services with an additional layer of protection for the user.

- **Geographic and Service Provider Information Extraction**: By using external databases like GeoLite2 and DBIP ASN, the script can obtain advanced information about the geographic location of IPs and their service provider, providing more detailed and valuable analysis.

- **Intelligent User-Agent Handling**: The automated user-agent cycle helps to avoid blocks and restrictions on servers that limit repetitive requests, allowing for more efficient and less detectable scraping.

- **Comprehensive Metadata Logging**: The script stores all relevant metadata of the analyzed IPs in a detailed SQLite database, such as titles, page descriptions, security policies, and more, facilitating later analysis and data-driven decision-making.

## Additional Strengths

- **Support for Large Networks**: Thanks to the ability to work with a large number of IP addresses at once, this code is ideal for those needing to perform security audits in large networks or distributed environments.

- **Automation and Customizable Configuration**: The use of command-line arguments and options for configuring timers, user agents, and protocols makes the tool highly configurable to adapt to various use cases.

- **Efficient Resource Management**: The code is optimized to utilize all available CPU cores, allowing for faster processing on multi-processor systems, significantly reducing execution times.

## Added Section: Ethical Use and Legal Considerations

This project is designed exclusively for use in authorized activities. It is the user's responsibility to ensure they have explicit permission to scan any network or system they wish to analyze. Unauthorized use of this tool may violate local and international laws and regulations. Its use must be strictly adhered to ethical and legal practices.

## Main Features

- **Massive IP Scanning**: Ability to scan large ranges of IP addresses using CIDR notation, facilitating large-scale assessments.
- **Optimized Performance**: Multi-threaded and multi-process implementation to maximize performance and minimize scan times.
- **Detailed Information Extraction**: Collection of comprehensive data from web servers (HTTP/HTTPS), including HTTP headers, HTML content, and server metadata.
- **Precise Geolocation**: Integrates GeoLite2 and DBIP ASN databases to provide detailed geolocation information of the scanned IPs.
- **SQLite Database**: Collected data is stored in SQLite databases, facilitating later querying, organizing, and analysis.
- **Guaranteed Anonymity**: All network requests are routed through the Tor network, ensuring anonymity protection and reducing the risk of detection.
- **User-Agent Rotation**: Implements a random user-agent rotation to avoid detection by automated defense mechanisms.
- **Adaptive Request Control**: Dynamically manages wait times between requests to prevent server overload and reduce the risk of blocking.

## Installation

To install IP2Domain, follow the steps below:

```bash
git clone https://github.com/N4rr34n6/IP2Domain.git
cd IP2Domain
pip3 install -r requirements.txt
```

## Prerequisites

- Python 3.x
- Tor (installed and running)
- Python libraries specified in requirements.txt
- GeoLite2 and DBIP ASN databases from MaxMind

## Usage

To start scanning with IP2Domain, use the following command:

```bash
python3 IP2Domain.py <ip_range_directory> <database_name>
```

## Additional Configuration

- User-agent rotation can be customized by modifying the list in the script.
- The `delay_range` values allow you to adjust the interval between requests to avoid overload or detection.

## Technical Details

- **IP Range Generation**: Uses the `ipaddress` module to generate IP addresses from CIDR notation ranges, optimizing analysis in large networks.
- **HTTP/HTTPS Scanning**: Establishes connections with web servers via HTTP and HTTPS protocols, maximizing detection and analysis of active servers.
- **Data Collection**: Extracts HTTP headers, HTML content, and server metadata to provide comprehensive information about detected servers.
- **Geolocation**: Integrates geolocation databases to provide accurate location data, using GeoLite2 and DBIP ASN databases.
- **Complete Anonymity**: Redirects all requests through the Tor network, preserving privacy and ensuring that the source of the scans remains hidden.
- **SQLite Storage**: All collected data is stored in SQLite databases, facilitating later analysis and efficient information management.
- **Error Handling**: Implements robust mechanisms for handling network, SSL, and other technical errors, ensuring scanning continuity.

## Ethical Use and Legal Considerations

The use of IP2Domain is strictly limited to authorized activities. Any use on networks or systems without proper consent may be illegal and can lead to serious legal consequences. Before using this tool, ensure you have explicit authorization from the owners of the networks and servers you plan to scan.

Users should respect the following recommendations:

- **Explicit Authorization**: Only use IP2Domain on networks and systems for which you have explicit permission from the owner or administrator.
- **Legal Compliance**: Ensure compliance with all local and international laws and regulations. Unauthorized use of this tool may violate cybersecurity laws, such as the CFAA (Computer Fraud and Abuse Act) or GDPR (General Data Protection Regulation).
- **Respect for Privacy**: Avoid any actions that compromise the privacy of individuals or entities.

Improper use of IP2Domain may result in legal consequences, such as civil lawsuits or criminal charges. The use is the sole responsibility of the user, who must ensure compliance with the law.

## Legal Notice

IP2Domain is provided "as is," without any explicit or implicit guarantee of functionality, security, or accuracy of results. The authors and contributors are not responsible for the misuse or illegal use of the tool. Users assume all responsibility for its use, including compliance with applicable legal and ethical regulations.

## License

This script is provided under the GNU Affero General Public License v3.0. You can find the full license text in the [LICENSE](LICENSE) file.
