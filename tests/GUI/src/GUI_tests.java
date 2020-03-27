import org.junit.jupiter.api.Test;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.firefox.FirefoxDriver;
import java.util.concurrent.TimeUnit;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class GUI_tests {
    @Test
    public void people_awards() throws InterruptedException {
        // execute the test <x = 0, y = 0, z = 0, submitButton = click> and check the output message is correct
        System.setProperty("webdriver.gecko.driver", "geckodriver");
        WebDriver wd = new FirefoxDriver(); // launch the browser
        wd.get("https://databaseengine.appspot.com/");
        WebElement we = wd.findElement(By.xpath("//*[contains(text(),'Splash')]"));
        we.click(); //click the button
        TimeUnit.SECONDS.sleep(2);
        we = wd.findElement(By.xpath("//*[contains(text(),'People')]"));
        we.click(); //click the button
        TimeUnit.SECONDS.sleep(2);
        we = wd.findElement(By.xpath("//*[contains(text(),'Bong Joon Ho')]"));
        we.click(); //click the button
        TimeUnit.SECONDS.sleep(2);
        we = wd.findElement(By.xpath("//*[contains(text(),'Awards')]"));
        we.click(); //click the button
        TimeUnit.SECONDS.sleep(2);
        we = wd.findElement(By.xpath("//*[contains(text(),'Actor in a leading Role')]"));
        we.click(); //click the button
        TimeUnit.SECONDS.sleep(10);
        we = wd.findElement(By.xpath("//*[contains(text(),'About')]"));
        we.click(); //click the button
        TimeUnit.SECONDS.sleep(2);
        wd.quit(); // close the browser window
    }
    @Test
    public void awards_people() throws InterruptedException {
        System.setProperty("webdriver.gecko.driver", "geckodriver");
        WebDriver wd = new FirefoxDriver(); // launch the browser
        wd.get("https://databaseengine.appspot.com/");
        WebElement we = wd.findElement(By.xpath("//*[contains(text(),'About')]"));
        we.click(); //click the button
        TimeUnit.SECONDS.sleep(2);
        we = wd.findElement(By.xpath("//*[contains(text(),'Awards')]"));
        we.click(); //click the button
        TimeUnit.SECONDS.sleep(2);
        we = wd.findElement(By.xpath("//*[contains(text(),'Actor in a leading Role')]"));
        we.click(); //click the button
        TimeUnit.SECONDS.sleep(10);
        we = wd.findElement(By.xpath("//*[contains(text(),'People')]"));
        we.click(); //click the button
        TimeUnit.SECONDS.sleep(2);
        we = wd.findElement(By.xpath("//*[contains(text(),'Janet Gaynor')]"));
        we.click(); //click the button
        TimeUnit.SECONDS.sleep(2);
        we = wd.findElement(By.xpath("//*[contains(text(),'Splash')]"));
        we.click(); //click the button
        TimeUnit.SECONDS.sleep(2);
        wd.quit(); // close the browser window
    }
    @Test
    public void years_movies() throws InterruptedException {
        System.setProperty("webdriver.gecko.driver", "geckodriver");
        WebDriver wd = new FirefoxDriver(); // launch the browser
        wd.get("https://databaseengine.appspot.com/");
        WebElement we = wd.findElement(By.xpath("//*[contains(text(),'About')]"));
        we.click(); //click the button
        TimeUnit.SECONDS.sleep(2);
        we = wd.findElement(By.xpath("//*[contains(text(),'Years')]"));
        we.click(); //click the button
        TimeUnit.SECONDS.sleep(2);
        we = wd.findElement(By.xpath("//*[contains(text(),'1995')]"));
        we.click(); //click the button
        TimeUnit.SECONDS.sleep(2);
        we = wd.findElement(By.xpath("//*[contains(text(),'Movies')]"));
        we.click(); //click the button
        TimeUnit.SECONDS.sleep(2);
        we = wd.findElement(By.xpath("//*[contains(text(),'Jojo Rabbit')]"));
        we.click(); //click the button
        TimeUnit.SECONDS.sleep(2);
        we = wd.findElement(By.xpath("//*[contains(text(),'Splash')]"));
        we.click(); //click the button
        TimeUnit.SECONDS.sleep(2);
        wd.quit(); // close the browser window
    }
    @Test
    public void movies_years() throws InterruptedException {
        System.setProperty("webdriver.gecko.driver", "geckodriver");
        WebDriver wd = new FirefoxDriver(); // launch the browser
        wd.get("https://databaseengine.appspot.com/");
        WebElement we = wd.findElement(By.xpath("//*[contains(text(),'Splash')]"));
        we.click(); //click the button
        TimeUnit.SECONDS.sleep(2);
        we = wd.findElement(By.xpath("//*[contains(text(),'Movies')]"));
        we.click(); //click the button
        TimeUnit.SECONDS.sleep(2);
        we = wd.findElement(By.xpath("//*[contains(text(),'Jojo Rabbit')]"));
        we.click(); //click the button
        TimeUnit.SECONDS.sleep(2);
        we = wd.findElement(By.xpath("//*[contains(text(),'Years')]"));
        we.click(); //click the button
        TimeUnit.SECONDS.sleep(2);
        we = wd.findElement(By.xpath("//*[contains(text(),'1996')]"));
        we.click(); //click the button
        TimeUnit.SECONDS.sleep(2);
        we = wd.findElement(By.xpath("//*[contains(text(),'About')]"));
        we.click(); //click the button
        TimeUnit.SECONDS.sleep(2);
        wd.quit(); // close the browser window
    }

}
